"""متن‌های دو زبانه (فارسی/انگلیسی)."""

from __future__ import annotations

from .config import settings

FA = {
    "start": (
        "👋 سلام <b>{name}</b>!\n\n"
        "من ویدیو (یا هر فایلی) را می‌گیرم و برایت یک <b>لینک دانلود مستقیم</b> می‌سازم.\n\n"
        "📤 کافیست ویدیو را برایم <b>فوروارد</b> یا ارسال کنی.\n"
        "🔗 لینک ساخته‌شده در هر دانلود‌منیجر، مرورگر یا IDM کار می‌کند.\n\n"
        "⚠️ به‌دلیل محدودیت Bot API تلگرام، حداکثر حجم فایل <b>{limit} مگابایت</b> است.\n\n"
        "برای راهنمای بیشتر /help را بزن."
    ),
    "help": (
        "📖 <b>راهنما</b>\n\n"
        "۱. ویدیو یا فایل را به من بفرست (فوروارد هم کافی است).\n"
        "۲. چند ثانیه صبر کن.\n"
        "۳. لینک دانلود مستقیم را دریافت کن.\n\n"
        "<b>دستورها</b>\n"
        "/start – شروع\n"
        "/help – همین راهنما\n"
        "/myfiles – آخرین فایل‌های تو\n"
        "/about – دربارهٔ ربات\n\n"
        "<b>نکات</b>\n"
        "• سقف حجم: {limit} مگابایت (محدودیت خودِ تلگرام)\n"
        "• لینک‌ها {ttl}\n"
        "• ویدیو، فایل، صوت، عکس و ویس پشتیبانی می‌شود."
    ),
    "about": (
        "🤖 <b>Video Direct Link Bot</b>\n"
        "نسخهٔ {version}\n\n"
        "متن‌باز، ساخته‌شده با aiogram و FastAPI و اجراشده روی Railway.\n"
        "هیچ فایلی روی سرور ذخیره نمی‌شود؛ دانلود مستقیماً از سرورهای تلگرام استریم می‌شود."
    ),
    "ttl_forever": "دائمی هستند و منقضی نمی‌شوند",
    "ttl_hours": "تا {hours} ساعت معتبرند",
    "processing": "⏳ در حال پردازش…",
    "no_file": (
        "🤔 اینجا فایلی ندیدم!\n\n"
        "لطفاً یک <b>ویدیو</b> یا <b>فایل</b> برایم بفرست یا فوروارد کن."
    ),
    "too_big": (
        "❌ <b>فایل خیلی بزرگ است</b>\n\n"
        "حجم فایل: <b>{size}</b>\n"
        "حداکثر مجاز: <b>{limit}</b>\n\n"
        "این محدودیتِ خودِ Telegram Bot API است و ربات‌ها نمی‌توانند فایل بزرگ‌تر از "
        "۲۰ مگابایت را دانلود کنند."
    ),
    "success": (
        "✅ <b>لینک دانلود آماده شد</b>\n\n"
        "📄 نام: <code>{name}</code>\n"
        "📦 حجم: <b>{size}</b>\n"
        "🕒 اعتبار: {ttl}\n\n"
        "🔗 <b>لینک مستقیم:</b>\n<code>{link}</code>\n\n"
        "<i>می‌توانی لینک را در IDM یا هر دانلودمنیجری بچسبانی.</i>"
    ),
    "btn_download": "⬇️ دانلود مستقیم",
    "btn_page": "🌐 صفحهٔ دانلود",
    "btn_copy": "📋 کپی لینک",
    "error": "❌ خطایی رخ داد:\n<code>{err}</code>\n\nلطفاً دوباره تلاش کن.",
    "rate_limited": "🚦 کمی آرام‌تر! لطفاً {sec} ثانیه صبر کن.",
    "not_allowed": "⛔️ شما اجازهٔ استفاده از این ربات را ندارید.",
    "join_channel": (
        "📢 برای استفاده از ربات ابتدا در کانال زیر عضو شو:\n{channel}\n\n"
        "بعد از عضویت دکمهٔ «بررسی عضویت» را بزن."
    ),
    "btn_join": "➕ عضویت در کانال",
    "btn_check": "🔄 بررسی عضویت",
    "joined_ok": "✅ عضویت تأیید شد! حالا ویدیو را بفرست.",
    "not_joined": "❌ هنوز عضو کانال نیستی.",
    "myfiles_empty": "📭 هنوز فایلی نفرستاده‌ای.",
    "myfiles_title": "🗂 <b>آخرین فایل‌های تو</b>\n\n",
    "stats": (
        "📊 <b>آمار ربات</b>\n\n"
        "👤 کاربران: <b>{users}</b> (۲۴ ساعت اخیر: {today_users})\n"
        "📁 فایل‌ها: <b>{files}</b> (۲۴ ساعت اخیر: {today_files})\n"
        "⬇️ دانلودها: <b>{downloads}</b>\n"
        "💾 حجم کل: <b>{bytes}</b>"
    ),
    "admin_only": "⛔️ این دستور فقط برای ادمین است.",
    "broadcast_usage": "استفاده: <code>/broadcast متن پیام</code>",
    "broadcast_done": "📣 ارسال شد به {ok} کاربر ({fail} ناموفق).",
}

EN = {
    "start": (
        "👋 Hi <b>{name}</b>!\n\n"
        "Send or forward me a video (or any file) and I'll give you a "
        "<b>direct download link</b>.\n\n"
        "⚠️ Telegram Bot API limits downloads to <b>{limit} MB</b>.\n\n"
        "Use /help for more."
    ),
    "help": (
        "📖 <b>Help</b>\n\n"
        "1. Send or forward a video/file.\n"
        "2. Wait a moment.\n"
        "3. Get your direct download link.\n\n"
        "<b>Commands</b>\n"
        "/start – start\n"
        "/help – this help\n"
        "/myfiles – your recent files\n"
        "/about – about this bot\n\n"
        "<b>Notes</b>\n"
        "• Max size: {limit} MB (Telegram limit)\n"
        "• Links {ttl}\n"
        "• Videos, documents, audio, photos and voice are supported."
    ),
    "about": (
        "🤖 <b>Video Direct Link Bot</b>\nv{version}\n\n"
        "Open source, built with aiogram + FastAPI, deployed on Railway.\n"
        "Nothing is stored on the server — downloads stream straight from Telegram."
    ),
    "ttl_forever": "never expire",
    "ttl_hours": "are valid for {hours} hours",
    "processing": "⏳ Processing…",
    "no_file": "🤔 I didn't find a file. Please send or forward a <b>video</b> or <b>document</b>.",
    "too_big": (
        "❌ <b>File too large</b>\n\nSize: <b>{size}</b>\nLimit: <b>{limit}</b>\n\n"
        "This is a hard Telegram Bot API limit (20 MB)."
    ),
    "success": (
        "✅ <b>Your download link is ready</b>\n\n"
        "📄 Name: <code>{name}</code>\n📦 Size: <b>{size}</b>\n🕒 Validity: {ttl}\n\n"
        "🔗 <b>Direct link:</b>\n<code>{link}</code>\n\n"
        "<i>Paste it into IDM or any download manager.</i>"
    ),
    "btn_download": "⬇️ Direct download",
    "btn_page": "🌐 Download page",
    "btn_copy": "📋 Copy link",
    "error": "❌ Something went wrong:\n<code>{err}</code>\n\nPlease try again.",
    "rate_limited": "🚦 Slow down! Please wait {sec}s.",
    "not_allowed": "⛔️ You are not allowed to use this bot.",
    "join_channel": "📢 Please join our channel first:\n{channel}",
    "btn_join": "➕ Join channel",
    "btn_check": "🔄 I've joined",
    "joined_ok": "✅ Verified! Now send me a video.",
    "not_joined": "❌ You haven't joined yet.",
    "myfiles_empty": "📭 You haven't sent any files yet.",
    "myfiles_title": "🗂 <b>Your recent files</b>\n\n",
    "stats": (
        "📊 <b>Bot stats</b>\n\n"
        "👤 Users: <b>{users}</b> (24h: {today_users})\n"
        "📁 Files: <b>{files}</b> (24h: {today_files})\n"
        "⬇️ Downloads: <b>{downloads}</b>\n💾 Total size: <b>{bytes}</b>"
    ),
    "admin_only": "⛔️ Admins only.",
    "broadcast_usage": "Usage: <code>/broadcast your message</code>",
    "broadcast_done": "📣 Sent to {ok} users ({fail} failed).",
}


def t(key: str, **kwargs) -> str:
    table = EN if settings.bot_lang == "en" else FA
    return table.get(key, FA.get(key, key)).format(**kwargs)
