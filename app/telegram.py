"""کلاینت سبک HTTP برای Telegram Bot API + استریم فایل.

نکتهٔ مهم: مقدار `file_path` که getFile برمی‌گرداند فقط حدود یک ساعت معتبر است،
اما `file_id` دائمی است. بنابراین هنگام هر دانلود دوباره getFile صدا زده می‌شود
تا لینک‌های ما همیشه کار کنند.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass

import httpx

from .config import settings

API_BASE = settings.telegram_api_base.rstrip("/")

_client: httpx.AsyncClient | None = None
# کش کوتاه‌مدت برای file_path (کاهش تعداد فراخوانی getFile)
_path_cache: dict[str, tuple[str, float]] = {}
_CACHE_TTL = 30 * 60  # ۳۰ دقیقه، محتاطانه‌تر از یک ساعتِ تلگرام


class TelegramError(Exception):
    def __init__(self, message: str, status: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status = status


@dataclass
class TgFile:
    file_id: str
    file_path: str
    file_size: int = 0

    @property
    def download_url(self) -> str:
        return f"{API_BASE}/file/bot{settings.bot_token}/{self.file_path}"


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=10.0, read=300.0, write=60.0, pool=10.0),
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
            follow_redirects=True,
        )
    return _client


async def close_client() -> None:
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
    _client = None


async def api_call(method: str, **params) -> dict:
    """فراخوانی متد Bot API با تلاش مجدد در خطاهای موقتی."""
    url = f"{API_BASE}/bot{settings.bot_token}/{method}"
    client = get_client()
    last_err: Exception | None = None

    for attempt in range(3):
        try:
            resp = await client.post(url, json=params)
            data = resp.json()
            if data.get("ok"):
                return data.get("result", {})

            desc = data.get("description", "unknown error")
            code = int(data.get("error_code", resp.status_code))

            # rate limit تلگرام
            if code == 429:
                retry_after = int(
                    data.get("parameters", {}).get("retry_after", 1 + attempt)
                )
                await asyncio.sleep(min(retry_after, 15))
                continue
            raise TelegramError(desc, code)
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            last_err = exc
            await asyncio.sleep(1.5 * (attempt + 1))

    raise TelegramError(f"ارتباط با تلگرام برقرار نشد: {last_err}", 502)


async def get_file(file_id: str, use_cache: bool = True) -> TgFile:
    """گرفتن file_path برای یک file_id."""
    now = time.time()
    if use_cache:
        cached = _path_cache.get(file_id)
        if cached and now - cached[1] < _CACHE_TTL:
            return TgFile(file_id=file_id, file_path=cached[0])

    result = await api_call("getFile", file_id=file_id)
    file_path = result.get("file_path")
    if not file_path:
        raise TelegramError("تلگرام مسیر فایل را برنگرداند", 404)

    _path_cache[file_id] = (file_path, now)
    if len(_path_cache) > 5000:  # جلوگیری از رشد بی‌نهایت
        for key in list(_path_cache)[:1000]:
            _path_cache.pop(key, None)

    return TgFile(
        file_id=file_id,
        file_path=file_path,
        file_size=int(result.get("file_size") or 0),
    )


async def open_stream(
    file_id: str, range_header: str | None = None
) -> tuple[httpx.Response, httpx.AsyncClient]:
    """باز کردن استریم دانلود از سرور تلگرام (با پشتیبانی Range).

    مسئولیت بستن پاسخ با فراخواننده است (`await response.aclose()`).
    """
    client = get_client()
    headers = {}
    if range_header:
        headers["Range"] = range_header

    for attempt in range(2):
        tg = await get_file(file_id, use_cache=(attempt == 0))
        request = client.build_request("GET", tg.download_url, headers=headers)
        response = await client.send(request, stream=True)

        if response.status_code in (200, 206):
            return response, client

        await response.aclose()
        # file_path منقضی شده؛ یک بار دیگر با getFile تازه تلاش کن
        if response.status_code in (400, 401, 403, 404) and attempt == 0:
            _path_cache.pop(file_id, None)
            continue
        raise TelegramError(
            f"دانلود از تلگرام ناموفق بود (HTTP {response.status_code})",
            response.status_code,
        )

    raise TelegramError("دانلود از تلگرام ناموفق بود", 502)


async def iter_stream(response: httpx.Response, chunk: int = 256 * 1024) -> AsyncIterator[bytes]:
    try:
        async for part in response.aiter_bytes(chunk):
            yield part
    finally:
        await response.aclose()
