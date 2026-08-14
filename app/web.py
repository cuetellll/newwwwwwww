"""وب‌سرور FastAPI: سرو کردن لینک‌های دانلود مستقیم + وبهوک تلگرام."""

from __future__ import annotations

import html
import logging

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse

from . import __version__
from .config import settings
from .db import db
from .telegram import TelegramError, get_file, iter_stream, open_stream
from .tokens import FilePayload, TokenError, parse_token
from .utils import content_disposition, human_size

log = logging.getLogger("web")
router = APIRouter()


# --------------------------------------------------------------------------- pages
def _page(title: str, body: str, status: int = 200) -> HTMLResponse:
    doc = f"""<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{html.escape(title)}</title>
<style>
  *{{box-sizing:border-box}}
  body{{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
       background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);
       font-family:system-ui,-apple-system,"Segoe UI",Tahoma,Vazirmatn,sans-serif;
       color:#e9eef3;padding:24px}}
  .card{{background:rgba(255,255,255,.07);backdrop-filter:blur(14px);
        border:1px solid rgba(255,255,255,.14);border-radius:20px;padding:32px;
        max-width:520px;width:100%;box-shadow:0 20px 60px rgba(0,0,0,.35);text-align:center}}
  h1{{margin:0 0 8px;font-size:22px;font-weight:700}}
  p{{margin:8px 0;color:#b9c6d2;font-size:14px;line-height:1.9}}
  .name{{word-break:break-all;font-weight:600;color:#fff;font-size:16px;margin:16px 0 4px}}
  .meta{{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin:18px 0}}
  .chip{{background:rgba(255,255,255,.1);border-radius:999px;padding:6px 14px;font-size:13px}}
  a.btn{{display:block;margin-top:20px;padding:15px 24px;border-radius:14px;
        background:linear-gradient(135deg,#2AABEE,#229ED9);color:#fff;text-decoration:none;
        font-weight:700;font-size:16px;transition:.2s;border:0}}
  a.btn:hover{{transform:translateY(-2px);box-shadow:0 10px 30px rgba(34,158,217,.45)}}
  .ghost{{background:rgba(255,255,255,.09);margin-top:10px}}
  .ico{{font-size:52px;margin-bottom:6px}}
  video{{width:100%;border-radius:14px;margin-top:16px;background:#000}}
  code{{background:rgba(0,0,0,.3);padding:8px 10px;border-radius:8px;display:block;
       word-break:break-all;font-size:12px;direction:ltr;text-align:left;margin-top:14px;color:#9fe3ff}}
  footer{{margin-top:20px;font-size:12px;color:#7f8fa0}}
</style>
</head>
<body><div class="card">{body}<footer>Telegram Direct Link Bot v{__version__}</footer></div></body>
</html>"""
    return HTMLResponse(doc, status_code=status)


def _error_page(message: str, status: int = 404) -> HTMLResponse:
    return _page(
        "خطا",
        f'<div class="ico">⚠️</div><h1>لینک در دسترس نیست</h1>'
        f"<p>{html.escape(message)}</p>",
        status,
    )


def _download_page(payload: FilePayload, direct_url: str) -> HTMLResponse:
    is_video = payload.mime.startswith("video/")
    preview = (
        f'<video controls preload="metadata" src="{html.escape(direct_url)}"></video>'
        if is_video else ""
    )
    icon = "🎬" if is_video else ("🖼" if payload.mime.startswith("image/") else "📦")
    size = human_size(payload.size) if payload.size else "نامشخص"
    body = f"""
      <div class="ico">{icon}</div>
      <h1>فایل شما آماده است</h1>
      <div class="name">{html.escape(payload.name)}</div>
      <div class="meta">
        <span class="chip">📦 {html.escape(size)}</span>
        <span class="chip">🏷 {html.escape(payload.mime)}</span>
      </div>
      {preview}
      <a class="btn" href="{html.escape(direct_url)}" download>⬇️ دانلود مستقیم</a>
      <a class="btn ghost" href="{html.escape(direct_url)}?inline=1" target="_blank">▶️ پخش در مرورگر</a>
      <code>{html.escape(direct_url)}</code>
      <p>این لینک را می‌توانید در IDM یا هر دانلودمنیجری استفاده کنید.</p>
    """
    return _page(payload.name, body)


# --------------------------------------------------------------------------- core
async def _stream_file(
    payload: FilePayload,
    request: Request,
    inline: bool = False,
    head_only: bool = False,
) -> Response:
    """دانلود را از سرور تلگرام به کاربر استریم می‌کند (بدون ذخیره روی دیسک)."""
    range_header = request.headers.get("range")

    if head_only:
        try:
            info = await get_file(payload.fid)
        except TelegramError as exc:
            return _error_page(exc.message, 502 if exc.status >= 500 else 404)
        size = payload.size or info.file_size
        headers = {
            "Content-Length": str(size or 0),
            "Content-Disposition": content_disposition(payload.name, inline),
            "Accept-Ranges": "bytes",
            "Content-Type": payload.mime,
        }
        return Response(status_code=200, headers=headers)

    try:
        upstream, _ = await open_stream(payload.fid, range_header)
    except TelegramError as exc:
        log.warning("stream failed: %s", exc)
        return _error_page(
            "فایل روی سرورهای تلگرام پیدا نشد یا دیگر در دسترس نیست.", 404
        )

    headers = {
        "Content-Disposition": content_disposition(payload.name, inline),
        "Accept-Ranges": "bytes",
        "Cache-Control": "public, max-age=3600",
        "X-Content-Type-Options": "nosniff",
    }
    for key in ("content-length", "content-range"):
        if key in upstream.headers:
            headers[key.title()] = upstream.headers[key]

    return StreamingResponse(
        iter_stream(upstream),
        status_code=upstream.status_code,
        media_type=payload.mime or upstream.headers.get("content-type"),
        headers=headers,
    )


async def _payload_from_slug(slug: str) -> FilePayload:
    row = await db.get_file(slug)
    if not row:
        raise HTTPException(status_code=404, detail="لینک نامعتبر است")
    payload = FilePayload(
        fid=row["file_id"],
        name=row["file_name"] or "download",
        size=row["file_size"] or 0,
        mime=row["mime"] or "application/octet-stream",
        exp=row["expires_at"] or 0,
        uid=row["user_id"] or 0,
    )
    if payload.is_expired():
        raise HTTPException(status_code=410, detail="این لینک منقضی شده است")
    return payload


# --------------------------------------------------------------------------- routes
@router.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    return _page(
        "Telegram Direct Link Bot",
        '<div class="ico">🎬</div><h1>ربات لینک مستقیم تلگرام</h1>'
        "<p>ویدیو را در تلگرام برای ربات فوروارد کنید تا لینک دانلود مستقیم بگیرید.</p>"
        "<p>این صفحه فقط سرویس‌دهندهٔ لینک‌هاست.</p>",
    )


@router.get("/health")
async def health() -> JSONResponse:
    return JSONResponse(
        {
            "ok": True,
            "version": __version__,
            "mode": "polling" if settings.use_polling else "webhook",
            "link_mode": settings.link_mode,
        }
    )


# --- حالت signed (بدون دیتابیس) ---
@router.api_route("/f/{token}/{filename}", methods=["GET", "HEAD"])
@router.api_route("/f/{token}", methods=["GET", "HEAD"])
async def download_signed(
    token: str, request: Request, filename: str | None = None
) -> Response:
    try:
        payload = parse_token(token)
    except TokenError as exc:
        return _error_page(str(exc), 410 if "منقضی" in str(exc) else 404)
    inline = request.query_params.get("inline") in {"1", "true", "yes"}
    return await _stream_file(payload, request, inline, request.method == "HEAD")


@router.get("/p/{token}", response_class=HTMLResponse)
async def page_signed(token: str) -> HTMLResponse:
    try:
        payload = parse_token(token)
    except TokenError as exc:
        return _error_page(str(exc), 410 if "منقضی" in str(exc) else 404)
    direct = f"{settings.public_base_url}/f/{token}/{payload.name}"
    return _download_page(payload, direct)


# --- حالت short (با دیتابیس) ---
@router.api_route("/dl/{slug}/{filename}", methods=["GET", "HEAD"])
@router.api_route("/dl/{slug}", methods=["GET", "HEAD"])
async def download_slug(
    slug: str, request: Request, filename: str | None = None
) -> Response:
    payload = await _payload_from_slug(slug)
    if request.method == "GET":
        try:
            await db.bump_download(slug)
        except Exception:  # noqa: BLE001
            pass
    inline = request.query_params.get("inline") in {"1", "true", "yes"}
    return await _stream_file(payload, request, inline, request.method == "HEAD")


@router.get("/d/{slug}", response_class=HTMLResponse)
async def page_slug(slug: str) -> HTMLResponse:
    try:
        payload = await _payload_from_slug(slug)
    except HTTPException as exc:
        return _error_page(str(exc.detail), exc.status_code)
    direct = f"{settings.public_base_url}/dl/{slug}/{payload.name}"
    return _download_page(payload, direct)


# --- وبهوک تلگرام ---
def build_webhook_router() -> APIRouter:
    """روتر وبهوک؛ bot/dispatcher در زمان درخواست از app.state خوانده می‌شوند."""
    from aiogram.types import Update

    hook = APIRouter()

    @hook.post(settings.effective_webhook_path, include_in_schema=False)
    async def telegram_webhook(  # noqa: ANN202
        request: Request,
        x_telegram_bot_api_secret_token: str | None = Header(default=None),
    ):
        if x_telegram_bot_api_secret_token != settings.webhook_secret:
            raise HTTPException(status_code=403, detail="forbidden")

        bot = request.app.state.bot
        dispatcher = request.app.state.dp
        data = await request.json()
        update = Update.model_validate(data, context={"bot": bot})
        await dispatcher.feed_update(bot, update)
        return {"ok": True}

    return hook
