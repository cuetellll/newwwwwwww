import os
import time

os.environ.setdefault("BOT_TOKEN", "123:TEST")
os.environ.setdefault("SECRET_KEY", "unit-test-secret-key-000000000000")
os.environ.setdefault("BASE_URL", "https://example.com")

import pytest  # noqa: E402

from app.tokens import FilePayload, TokenError, make_token, parse_token  # noqa: E402
from app.utils import (  # noqa: E402
    RateLimiter,
    content_disposition,
    ensure_extension,
    human_size,
    safe_filename,
)


def test_roundtrip():
    p = FilePayload(fid="BAADAgAD", name="my video.mp4", size=12345,
                    mime="video/mp4", exp=0, uid=42)
    back = parse_token(make_token(p))
    assert back.fid == p.fid
    assert back.name == p.name
    assert back.size == p.size


def test_tampered_token_rejected():
    token = make_token(FilePayload(fid="abc"))
    body, sig = token.split(".")
    with pytest.raises(TokenError):
        parse_token(body[:-2] + "xx." + sig)


def test_expired_token():
    p = FilePayload(fid="abc", exp=int(time.time()) - 10)
    with pytest.raises(TokenError):
        parse_token(make_token(p))


def test_no_expiry_means_permanent():
    p = FilePayload(fid="abc", exp=0)
    assert parse_token(make_token(p)).is_expired() is False


def test_human_size():
    assert human_size(0) == "0 B"
    assert human_size(1024) == "1.00 KB"
    assert human_size(1024 * 1024) == "1.00 MB"


def test_safe_filename():
    assert safe_filename("../../etc/passwd") == "etc_passwd"
    assert safe_filename("") == "video.mp4"
    assert safe_filename("ویدیو من.mp4") == "ویدیو من.mp4"
    assert len(safe_filename("a" * 500 + ".mp4")) <= 120


def test_ensure_extension():
    assert ensure_extension("movie", "video/mp4") == "movie.mp4"
    assert ensure_extension("movie.mkv", "video/mp4") == "movie.mkv"


def test_content_disposition_utf8():
    header = content_disposition("ویدیو.mp4")
    assert "attachment" in header
    assert "filename*=UTF-8''" in header


def test_rate_limiter():
    rl = RateLimiter(limit=3, window=60)
    assert all(rl.check(1)[0] for _ in range(3))
    allowed, wait = rl.check(1)
    assert allowed is False and wait > 0
    assert rl.check(2)[0] is True
