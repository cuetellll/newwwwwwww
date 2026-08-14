"""تنظیمات برنامه؛ همه چیز از متغیرهای محیطی خوانده می‌شود."""

from __future__ import annotations

import hashlib
import os
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _split_ids(raw: str | list[int] | None) -> list[int]:
    if not raw:
        return []
    if isinstance(raw, list):
        return [int(x) for x in raw]
    out: list[int] = []
    for part in str(raw).replace(";", ",").split(","):
        part = part.strip()
        if not part:
            continue
        try:
            out.append(int(part))
        except ValueError:
            continue
    return out


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- الزامی ---
    bot_token: str = Field(default="", alias="BOT_TOKEN")
    base_url: str = Field(default="", alias="BASE_URL")
    secret_key: str = Field(default="", alias="SECRET_KEY")

    # --- اختیاری ---
    mode: str = Field(default="webhook", alias="MODE")  # webhook | polling
    webhook_path: str = Field(default="", alias="WEBHOOK_PATH")
    port: int = Field(default=8080, alias="PORT")
    host: str = Field(default="0.0.0.0", alias="HOST")
    bot_lang: str = Field(default="fa", alias="BOT_LANG")

    admin_ids: list[int] = Field(default_factory=list, alias="ADMIN_IDS")
    allowed_user_ids: list[int] = Field(default_factory=list, alias="ALLOWED_USER_IDS")
    required_channel: str = Field(default="", alias="REQUIRED_CHANNEL")

    link_mode: str = Field(default="signed", alias="LINK_MODE")  # signed | short
    link_ttl_hours: int = Field(default=0, alias="LINK_TTL_HOURS")

    data_dir: str = Field(default="./data", alias="DATA_DIR")
    rate_limit_per_minute: int = Field(default=20, alias="RATE_LIMIT_PER_MINUTE")
    max_file_size_mb: int = Field(default=20, alias="MAX_FILE_SIZE_MB")

    # آدرس Bot API؛ فقط اگر سرور محلی Telegram Bot API دارید تغییر دهید
    telegram_api_base: str = Field(
        default="https://api.telegram.org", alias="TELEGRAM_API_BASE"
    )

    # Railway این متغیر را خودکار ست می‌کند
    railway_public_domain: str = Field(default="", alias="RAILWAY_PUBLIC_DOMAIN")

    @field_validator("admin_ids", "allowed_user_ids", mode="before")
    @classmethod
    def _parse_ids(cls, v):  # noqa: D102
        return _split_ids(v)

    @field_validator("bot_lang", mode="before")
    @classmethod
    def _lang(cls, v):
        v = (v or "fa").strip().lower()
        return v if v in {"fa", "en"} else "fa"

    @field_validator("mode", "link_mode", mode="before")
    @classmethod
    def _lower(cls, v):
        return (v or "").strip().lower()

    # ------------------------------------------------------------------
    @property
    def public_base_url(self) -> str:
        """آدرس عمومی سرویس، بدون اسلش انتهایی."""
        url = (self.base_url or "").strip().rstrip("/")
        if not url and self.railway_public_domain:
            url = f"https://{self.railway_public_domain.strip().rstrip('/')}"
        if url and not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url

    @property
    def effective_webhook_path(self) -> str:
        if self.webhook_path:
            return "/" + self.webhook_path.strip("/")
        digest = hashlib.sha256(
            (self.secret_key + "|" + self.bot_token).encode()
        ).hexdigest()[:32]
        return f"/webhook/{digest}"

    @property
    def webhook_url(self) -> str:
        return f"{self.public_base_url}{self.effective_webhook_path}"

    @property
    def webhook_secret(self) -> str:
        """مقدار هدر X-Telegram-Bot-Api-Secret-Token."""
        return hashlib.sha256(
            ("wh-secret|" + self.secret_key).encode()
        ).hexdigest()[:48]

    @property
    def max_file_size_bytes(self) -> int:
        return max(1, self.max_file_size_mb) * 1024 * 1024

    @property
    def db_path(self) -> str:
        os.makedirs(self.data_dir, exist_ok=True)
        return os.path.join(self.data_dir, "bot.db")

    @property
    def use_polling(self) -> bool:
        return self.mode == "polling" or not self.public_base_url

    def validate_runtime(self) -> None:
        missing = []
        if not self.bot_token:
            missing.append("BOT_TOKEN")
        if not self.secret_key:
            missing.append("SECRET_KEY")
        if missing:
            raise RuntimeError(
                "متغیرهای محیطی الزامی تنظیم نشده‌اند: " + ", ".join(missing)
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
