"""ابزارهای کمکی: فرمت حجم، پاک‌سازی نام فایل، محدودیت نرخ."""

from __future__ import annotations

import re
import time
import unicodedata
from collections import defaultdict, deque
from urllib.parse import quote

_SAFE_RE = re.compile(r"[^A-Za-z0-9._\-\u0600-\u06FF ]+")
_MULTI_DOT = re.compile(r"\.{2,}")


def human_size(num: float) -> str:
    """۱۰۴۸۵۷۶ -> '1.0 MB'"""
    if num is None:
        return "?"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num) < 1024.0 or unit == "TB":
            if unit == "B":
                return f"{int(num)} {unit}"
            return f"{num:.2f} {unit}"
        num /= 1024.0
    return f"{num:.2f} TB"


def safe_filename(name: str, default: str = "video.mp4", max_len: int = 120) -> str:
    """نام فایل امن برای هدر Content-Disposition."""
    name = (name or "").strip()
    if not name:
        return default
    name = unicodedata.normalize("NFKC", name)
    name = name.replace("/", "_").replace("\\", "_").replace("\x00", "")
    name = _SAFE_RE.sub("_", name)
    name = _MULTI_DOT.sub(".", name).strip("._ ")
    if not name:
        return default
    if len(name) > max_len:
        head, _, ext = name.rpartition(".")
        if head and len(ext) <= 8:
            name = head[: max_len - len(ext) - 1] + "." + ext
        else:
            name = name[:max_len]
    return name


def ensure_extension(name: str, mime: str) -> str:
    """اگر فایل پسوند نداشت، از روی mime یک پسوند منطقی اضافه کن."""
    if "." in name.strip("."):
        return name
    mapping = {
        "video/mp4": ".mp4",
        "video/quicktime": ".mov",
        "video/x-matroska": ".mkv",
        "video/webm": ".webm",
        "video/x-msvideo": ".avi",
        "audio/mpeg": ".mp3",
        "audio/ogg": ".ogg",
        "audio/mp4": ".m4a",
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "application/pdf": ".pdf",
        "application/zip": ".zip",
    }
    return name + mapping.get(mime, ".bin")


def content_disposition(filename: str, inline: bool = False) -> str:
    """هدر Content-Disposition سازگار با RFC 5987 (پشتیبانی از نام فارسی).

    مرورگرهای قدیمی از `filename` اسکی استفاده می‌کنند و مدرن‌ها از `filename*`.
    اگر نام کاملاً غیر اسکی باشد (مثلاً فارسی) یک نام جایگزین امن می‌سازیم.
    """
    disp = "inline" if inline else "attachment"

    stem, dot, ext = filename.rpartition(".")
    if not dot:  # بدون پسوند
        stem, ext = filename, ""
    ext = re.sub(r"[^A-Za-z0-9]", "", ext)[:8]

    ascii_stem = stem.encode("ascii", "ignore").decode()
    ascii_stem = re.sub(r'[\\"\x00-\x1f]', "", ascii_stem)
    ascii_stem = re.sub(r"\s+", "_", ascii_stem).strip("._ ")

    if not ascii_stem:  # نام کاملاً غیر اسکی بود (مثلاً فارسی)
        ascii_stem = "download"

    ascii_name = f"{ascii_stem}.{ext}" if ext else ascii_stem

    return f"{disp}; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(filename)}"


def guess_mime(name: str, fallback: str = "application/octet-stream") -> str:
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    return {
        "mp4": "video/mp4",
        "mov": "video/quicktime",
        "mkv": "video/x-matroska",
        "webm": "video/webm",
        "avi": "video/x-msvideo",
        "mp3": "audio/mpeg",
        "m4a": "audio/mp4",
        "ogg": "audio/ogg",
        "oga": "audio/ogg",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
        "gif": "image/gif",
        "pdf": "application/pdf",
        "zip": "application/zip",
    }.get(ext, fallback)


class RateLimiter:
    """محدودکنندهٔ ساده و درون‌حافظه‌ای بر پایهٔ پنجرهٔ لغزان."""

    def __init__(self, limit: int = 20, window: int = 60) -> None:
        self.limit = max(1, limit)
        self.window = window
        self._hits: dict[int, deque[float]] = defaultdict(deque)

    def check(self, key: int) -> tuple[bool, int]:
        """(اجازه‌دارد، ثانیهٔ باقی‌مانده)"""
        now = time.time()
        q = self._hits[key]
        while q and now - q[0] > self.window:
            q.popleft()
        if len(q) >= self.limit:
            return False, max(1, int(self.window - (now - q[0])))
        q.append(now)
        return True, 0
