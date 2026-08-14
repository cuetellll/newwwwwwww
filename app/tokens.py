"""ساخت و اعتبارسنجی توکن امضاشدهٔ لینک دانلود.

قالب توکن:  base64url(payload_json_gzip) + "." + base64url(hmac_sha256)
داخل payload اطلاعات فایل (file_id، نام، حجم، mime و زمان انقضا) قرار دارد،
بنابراین برای حالت `signed` هیچ دیتابیسی لازم نیست و لینک‌ها دائمی‌اند.
"""

from __future__ import annotations

import base64
import gzip
import hmac
import json
import time
from dataclasses import asdict, dataclass
from hashlib import sha256

from .config import settings


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _b64d(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


def _sign(raw: bytes) -> bytes:
    return hmac.new(settings.secret_key.encode(), raw, sha256).digest()


@dataclass
class FilePayload:
    """اطلاعات فایل که داخل لینک ذخیره می‌شود."""

    fid: str                      # file_id تلگرام
    name: str = "video.mp4"       # نام پیشنهادی فایل
    size: int = 0                 # حجم بر حسب بایت
    mime: str = "application/octet-stream"
    exp: int = 0                  # unix timestamp، صفر = بدون انقضا
    uid: int = 0                  # آیدی کاربر سازنده (برای آمار)

    def is_expired(self) -> bool:
        return bool(self.exp) and time.time() > self.exp


class TokenError(Exception):
    """توکن نامعتبر یا منقضی."""


def make_token(payload: FilePayload) -> str:
    raw = gzip.compress(
        json.dumps(asdict(payload), separators=(",", ":"), ensure_ascii=False).encode()
    )
    return f"{_b64e(raw)}.{_b64e(_sign(raw))}"


def parse_token(token: str) -> FilePayload:
    try:
        body_b64, sig_b64 = token.split(".", 1)
        raw = _b64d(body_b64)
        sig = _b64d(sig_b64)
    except Exception as exc:  # noqa: BLE001
        raise TokenError("قالب توکن نامعتبر است") from exc

    if not hmac.compare_digest(sig, _sign(raw)):
        raise TokenError("امضای توکن نامعتبر است")

    try:
        data = json.loads(gzip.decompress(raw).decode())
        payload = FilePayload(**data)
    except Exception as exc:  # noqa: BLE001
        raise TokenError("محتوای توکن خراب است") from exc

    if payload.is_expired():
        raise TokenError("این لینک منقضی شده است")
    return payload


def expiry_timestamp(ttl_hours: int | None = None) -> int:
    hours = settings.link_ttl_hours if ttl_hours is None else ttl_hours
    if hours <= 0:
        return 0
    return int(time.time()) + hours * 3600
