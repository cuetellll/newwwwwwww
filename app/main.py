"""نقطهٔ ورود برنامه: FastAPI + ربات تلگرام در یک پروسه."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from . import __version__
from .bot import build_dispatcher, get_bot
from .config import settings
from .db import db
from .telegram import close_client
from .web import build_webhook_router
from .web import router as web_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
log = logging.getLogger("main")

_polling_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201
    global _polling_task
    settings.validate_runtime()

    await db.connect()
    log.info("دیتابیس آماده شد: %s", settings.db_path)

    bot = get_bot()
    dp = build_dispatcher()
    app.state.bot = bot
    app.state.dp = dp

    # اتصال به تلگرام نباید مانع بالا آمدن وب‌سرور شود؛ اگر تلگرام موقتاً در
    # دسترس نباشد، لینک‌های دانلودِ قبلی باید همچنان کار کنند.
    try:
        me = await bot.get_me()
        log.info("ربات متصل شد: @%s (id=%s)", me.username, me.id)

        if settings.use_polling:
            log.warning("حالت polling فعال است (برای Railway توصیه نمی‌شود)")
            await bot.delete_webhook(drop_pending_updates=True)
            _polling_task = asyncio.create_task(
                dp.start_polling(bot, handle_signals=False)
            )
        else:
            await bot.set_webhook(
                url=settings.webhook_url,
                secret_token=settings.webhook_secret,
                drop_pending_updates=True,
                allowed_updates=["message", "edited_message", "callback_query"],
            )
            log.info("وبهوک تنظیم شد: %s", settings.webhook_url)
    except Exception as exc:  # noqa: BLE001
        log.error(
            "راه‌اندازی ربات ناموفق بود (%s). وب‌سرور بالا می‌آید ولی ربات پاسخ نمی‌دهد؛ "
            "BOT_TOKEN و BASE_URL را بررسی کنید.",
            exc,
        )

    try:
        yield
    finally:
        log.info("در حال خاموش شدن…")
        if _polling_task:
            _polling_task.cancel()
            try:
                await _polling_task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass
        try:
            await bot.session.close()
        except Exception:  # noqa: BLE001
            pass
        await close_client()
        await db.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Telegram Video Direct Link Bot",
        version=__version__,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )

    app.include_router(web_router)

    if not settings.use_polling:
        app.include_router(build_webhook_router())

    return app


app = create_app()


def main() -> None:
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_level="info",
        access_log=False,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    main()
