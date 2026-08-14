"""منطق ربات تلگرام (aiogram v3)."""

from __future__ import annotations

import hashlib
import logging
import secrets

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from . import __version__
from .config import settings
from .db import db
from .texts import t
from .tokens import FilePayload, expiry_timestamp, make_token
from .utils import RateLimiter, ensure_extension, guess_mime, human_size, safe_filename

log = logging.getLogger("bot")
router = Router()
limiter = RateLimiter(limit=settings.rate_limit_per_minute, window=60)

_bot: Bot | None = None


def get_bot() -> Bot:
    global _bot
    if _bot is None:
        settings.validate_runtime()
        session = None
        # پشتیبانی از سرور محلی Telegram Bot API (اختیاری)
        if settings.telegram_api_base.rstrip("/") != "https://api.telegram.org":
            from aiogram.client.session.aiohttp import AiohttpSession
            from aiogram.client.telegram import TelegramAPIServer

            base = settings.telegram_api_base.rstrip("/")
            session = AiohttpSession(
                api=TelegramAPIServer(
                    base=f"{base}/bot{{token}}/{{method}}",
                    file=f"{base}/file/bot{{token}}/{{path}}",
                )
            )
        _bot = Bot(
            token=settings.bot_token,
            session=session,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
    return _bot


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(router)
    return dp


# --------------------------------------------------------------------------- helpers
def ttl_text() -> str:
    if settings.link_ttl_hours <= 0:
        return t("ttl_forever")
    return t("ttl_hours", hours=settings.link_ttl_hours)


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


def _slug(file_unique_id: str, user_id: int) -> str:
    base = f"{file_unique_id}|{user_id}|{settings.secret_key}"
    return hashlib.sha256(base.encode()).hexdigest()[:12] + secrets.token_urlsafe(3)


async def check_membership(user_id: int) -> bool:
    """بررسی عضویت در کانال اجباری."""
    if not settings.required_channel:
        return True
    try:
        member = await get_bot().get_chat_member(settings.required_channel, user_id)
        return member.status in {"creator", "administrator", "member"}
    except Exception as exc:  # noqa: BLE001
        log.warning("check_membership failed: %s", exc)
        return True  # اگر ربات ادمین کانال نباشد، جلوی کاربر را نمی‌گیریم


def join_keyboard() -> InlineKeyboardMarkup:
    ch = settings.required_channel.lstrip("@")
    url = f"https://t.me/{ch}" if not settings.required_channel.startswith("-") else ""
    rows = []
    if url:
        rows.append([InlineKeyboardButton(text=t("btn_join"), url=url)])
    rows.append([InlineKeyboardButton(text=t("btn_check"), callback_data="check_join")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def guard(message: Message) -> bool:
    """بررسی دسترسی، محدودیت نرخ و عضویت. True یعنی اجازه هست."""
    user = message.from_user
    if user is None:
        return False

    if settings.allowed_user_ids and user.id not in settings.allowed_user_ids:
        await message.answer(t("not_allowed"))
        return False

    ok, wait = limiter.check(user.id)
    if not ok:
        await message.answer(t("rate_limited", sec=wait))
        return False

    if not await check_membership(user.id):
        await message.answer(
            t("join_channel", channel=settings.required_channel),
            reply_markup=join_keyboard(),
            disable_web_page_preview=True,
        )
        return False

    try:
        await db.upsert_user(
            user.id, user.username, user.first_name, user.language_code
        )
    except Exception as exc:  # noqa: BLE001
        log.debug("upsert_user skipped: %s", exc)
    return True


def extract_media(message: Message) -> tuple[str, str, str, int, str] | None:
    """(file_id, file_unique_id, file_name, file_size, mime) یا None."""
    if message.video:
        v = message.video
        name = safe_filename(v.file_name or f"video_{v.file_unique_id}.mp4")
        mime = v.mime_type or guess_mime(name, "video/mp4")
        return v.file_id, v.file_unique_id, ensure_extension(name, mime), v.file_size or 0, mime

    if message.document:
        d = message.document
        name = safe_filename(d.file_name or f"file_{d.file_unique_id}")
        mime = d.mime_type or guess_mime(name)
        return d.file_id, d.file_unique_id, ensure_extension(name, mime), d.file_size or 0, mime

    if message.animation:
        a = message.animation
        name = safe_filename(a.file_name or f"animation_{a.file_unique_id}.mp4")
        mime = a.mime_type or "video/mp4"
        return a.file_id, a.file_unique_id, ensure_extension(name, mime), a.file_size or 0, mime

    if message.audio:
        a = message.audio
        name = safe_filename(a.file_name or f"{a.title or 'audio'}_{a.file_unique_id}.mp3")
        mime = a.mime_type or "audio/mpeg"
        return a.file_id, a.file_unique_id, ensure_extension(name, mime), a.file_size or 0, mime

    if message.voice:
        v = message.voice
        mime = v.mime_type or "audio/ogg"
        name = f"voice_{v.file_unique_id}.ogg"
        return v.file_id, v.file_unique_id, name, v.file_size or 0, mime

    if message.video_note:
        v = message.video_note
        return v.file_id, v.file_unique_id, f"video_note_{v.file_unique_id}.mp4", v.file_size or 0, "video/mp4"

    if message.photo:
        p = message.photo[-1]  # بزرگ‌ترین نسخه
        return p.file_id, p.file_unique_id, f"photo_{p.file_unique_id}.jpg", p.file_size or 0, "image/jpeg"

    if message.sticker:
        s = message.sticker
        ext = ".webm" if s.is_video else (".tgs" if s.is_animated else ".webp")
        return s.file_id, s.file_unique_id, f"sticker_{s.file_unique_id}{ext}", s.file_size or 0, guess_mime(ext)

    return None


def result_keyboard(direct: str, page: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_download"), url=direct)],
            [InlineKeyboardButton(text=t("btn_page"), url=page)],
        ]
    )


# --------------------------------------------------------------------------- commands
@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    if not await guard(message):
        return
    await message.answer(
        t("start",
          name=(message.from_user.first_name if message.from_user else "کاربر"),
          limit=settings.max_file_size_mb)
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    if not await guard(message):
        return
    await message.answer(t("help", limit=settings.max_file_size_mb, ttl=ttl_text()))


@router.message(Command("about"))
async def cmd_about(message: Message) -> None:
    await message.answer(t("about", version=__version__))


@router.message(Command("myfiles"))
async def cmd_myfiles(message: Message) -> None:
    if not await guard(message):
        return
    rows = await db.user_files(message.from_user.id, limit=10)
    if not rows:
        await message.answer(t("myfiles_empty"))
        return
    lines = [t("myfiles_title")]
    for i, r in enumerate(rows, 1):
        link = f"{settings.public_base_url}/d/{r['slug']}"
        lines.append(
            f"{i}. <b>{r['file_name']}</b> — {human_size(r['file_size'])}\n"
            f"   ⬇️ {r['downloads']} | <code>{link}</code>\n"
        )
    await message.answer("\n".join(lines), disable_web_page_preview=True)


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    if not is_admin(message.from_user.id):
        await message.answer(t("admin_only"))
        return
    s = await db.stats()
    await message.answer(
        t("stats",
          users=s["users"], today_users=s["today_users"],
          files=s["files"], today_files=s["today_files"],
          downloads=s["downloads"], bytes=human_size(s["bytes"]))
    )


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message) -> None:
    if not is_admin(message.from_user.id):
        await message.answer(t("admin_only"))
        return
    text = (message.text or "").partition(" ")[2].strip()
    if not text:
        await message.answer(t("broadcast_usage"))
        return
    ok = fail = 0
    for uid in await db.all_user_ids():
        try:
            await get_bot().send_message(uid, text)
            ok += 1
        except Exception:  # noqa: BLE001
            fail += 1
    await message.answer(t("broadcast_done", ok=ok, fail=fail))


@router.callback_query(F.data == "check_join")
async def cb_check_join(call: CallbackQuery) -> None:
    if await check_membership(call.from_user.id):
        await call.message.edit_text(t("joined_ok"))
    else:
        await call.answer(t("not_joined"), show_alert=True)


# --------------------------------------------------------------------------- media
@router.message(
    F.video | F.document | F.animation | F.audio | F.voice | F.video_note
    | F.photo | F.sticker
)
async def handle_media(message: Message) -> None:
    if not await guard(message):
        return

    media = extract_media(message)
    if not media:
        await message.answer(t("no_file"))
        return

    file_id, file_unique_id, file_name, file_size, mime = media

    if file_size and file_size > settings.max_file_size_bytes:
        await message.answer(
            t("too_big",
              size=human_size(file_size),
              limit=f"{settings.max_file_size_mb} MB")
        )
        return

    status = await message.answer(t("processing"))
    try:
        exp = expiry_timestamp()
        payload = FilePayload(
            fid=file_id,
            name=file_name,
            size=file_size,
            mime=mime,
            exp=exp,
            uid=message.from_user.id,
        )

        if settings.link_mode == "short":
            slug = _slug(file_unique_id, message.from_user.id)
            await db.save_file(
                slug, file_id, file_name, file_size, mime, message.from_user.id, exp
            )
            direct = f"{settings.public_base_url}/dl/{slug}/{file_name}"
            page = f"{settings.public_base_url}/d/{slug}"
        else:
            token = make_token(payload)
            direct = f"{settings.public_base_url}/f/{token}/{file_name}"
            page = f"{settings.public_base_url}/p/{token}"
            # ثبت در دیتابیس فقط برای آمار (لینک به آن وابسته نیست)
            try:
                await db.save_file(
                    _slug(file_unique_id, message.from_user.id),
                    file_id, file_name, file_size, mime, message.from_user.id, exp,
                )
            except Exception as exc:  # noqa: BLE001
                log.debug("stats save skipped: %s", exc)

        await status.edit_text(
            t("success",
              name=file_name,
              size=human_size(file_size) if file_size else "?",
              ttl=ttl_text(),
              link=direct),
            reply_markup=result_keyboard(direct, page),
            disable_web_page_preview=True,
        )
    except Exception as exc:  # noqa: BLE001
        log.exception("handle_media failed")
        await status.edit_text(t("error", err=str(exc)[:300]))


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text(message: Message) -> None:
    if not await guard(message):
        return
    await message.answer(t("no_file"))
