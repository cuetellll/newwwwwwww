"""تست‌های تنظیمات، به‌ویژه خواندن مقاومِ PORT.

پس‌زمینه: Railway مقدار startCommand را بدون شل اجرا می‌کند، بنابراین اگر در
دستور اجرا از `$PORT` استفاده شود، رشتهٔ خام به برنامه می‌رسد و uvicorn با
«Invalid value for '--port'» کرش می‌کند. این تست‌ها تضمین می‌کنند که برنامه
به‌جای کرش، به پورت پیش‌فرض برگردد.
"""

import os

os.environ.setdefault("BOT_TOKEN", "123:TEST")
os.environ.setdefault("SECRET_KEY", "unit-test-secret-key-000000000000")

import pytest  # noqa: E402

from app.config import Settings  # noqa: E402


def make(**env) -> Settings:
    return Settings(**env)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("8080", 8080),
        (3000, 3000),
        ("  3000  ", 3000),
        ('"8080"', 8080),
        ("$PORT", 8080),        # شل مقدار را باز نکرده
        ("${{PORT}}", 8080),    # قالب متغیر Railway
        ("", 8080),
        ("abc", 8080),
        ("0", 8080),
        ("99999", 8080),        # خارج از محدودهٔ مجاز
        (None, 8080),
    ],
)
def test_port_is_parsed_safely(raw, expected):
    assert make(PORT=raw).port == expected


def test_railway_domain_becomes_base_url():
    s = make(BASE_URL="", RAILWAY_PUBLIC_DOMAIN="my-app.up.railway.app")
    assert s.public_base_url == "https://my-app.up.railway.app"


def test_base_url_gets_scheme_and_strips_slash():
    assert make(BASE_URL="example.com/").public_base_url == "https://example.com"


def test_webhook_path_is_secret_and_stable():
    a, b = make(BASE_URL="https://e.com"), make(BASE_URL="https://e.com")
    assert a.effective_webhook_path == b.effective_webhook_path
    assert a.effective_webhook_path.startswith("/webhook/")


def test_custom_webhook_path_normalised():
    assert make(WEBHOOK_PATH="hook").effective_webhook_path == "/hook"


def test_admin_ids_parsing():
    assert make(ADMIN_IDS="111, 222 ,bad,333").admin_ids == [111, 222, 333]
    assert make(ADMIN_IDS="").admin_ids == []


def test_polling_when_no_public_url():
    assert make(MODE="webhook", BASE_URL="", RAILWAY_PUBLIC_DOMAIN="").use_polling is True
    assert make(MODE="webhook", BASE_URL="https://e.com").use_polling is False
