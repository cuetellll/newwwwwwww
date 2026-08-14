<div dir="rtl">

# 🎬 ربات لینک دانلود مستقیم تلگرام

رباتی که کاربر در تلگرام برایش **ویدیو فوروارد می‌کند** و ربات یک **لینک دانلود مستقیم** تحویل می‌دهد — قابل استفاده در مرورگر، IDM و هر دانلودمنیجری.

ساخته‌شده با **aiogram v3 + FastAPI**، آمادهٔ استقرار روی **Railway**.

</div>

```
کاربر ─(فوروارد ویدیو)─▶ ربات ─▶ https://your-app.up.railway.app/f/<token>/video.mp4
```

<div dir="rtl">

## ✨ امکانات

| ویژگی | توضیح |
|---|---|
| 🔗 **لینک دائمی** | لینک‌ها منقضی نمی‌شوند (قابل تنظیم) و به دیتابیس وابسته نیستند |
| ⚡️ **بدون ذخیره‌سازی** | فایل روی سرور ذخیره نمی‌شود؛ مستقیماً از تلگرام استریم می‌شود (دیسک صفر) |
| ⏯ **پشتیبانی Range** | ادامهٔ دانلود قطع‌شده، دانلود چندبخشی IDM و seek در ویدیو |
| 🔐 **لینک امضاشده** | HMAC-SHA256؛ لینک دستکاری‌شده کار نمی‌کند |
| 🌐 **صفحهٔ دانلود** | صفحهٔ زیبا با پیش‌نمایش ویدیو و دکمهٔ دانلود |
| 📁 **همه نوع فایل** | ویدیو، داکیومنت، صوت، ویس، عکس، ویدیونوت، استیکر، گیف |
| 🇮🇷 **دو زبانه** | فارسی و انگلیسی (`BOT_LANG`) |
| 🛡 **کنترل دسترسی** | محدودیت نرخ، لیست کاربران مجاز، عضویت اجباری در کانال |
| 📊 **پنل آمار** | `/stats` و `/broadcast` برای ادمین |
| 🪝 **وبهوک امن** | مسیر مخفی + هدر `X-Telegram-Bot-Api-Secret-Token` |
| ✅ **تست‌شده** | ۱۷ تست خودکار + CI گیت‌هاب |

## ⚠️ مهم: محدودیت ۲۰ مگابایت

Telegram **Bot API** اجازه نمی‌دهد ربات‌ها فایل بزرگ‌تر از **۲۰ مگابایت** دانلود کنند. این محدودیتِ خودِ تلگرام است، نه این کد.

برای فایل‌های بزرگ‌تر (تا ۲ گیگابایت) باید یک **سرور محلی Telegram Bot API** اجرا کنید. کد از آن پشتیبانی می‌کند — کافی است `TELEGRAM_API_BASE` را به آدرس سرور خودتان تغییر دهید. (بخش «فایل‌های بزرگ» را ببینید.)

---

## 🚀 استقرار روی Railway (گام‌به‌گام)

### ۱. ساخت ربات در تلگرام
۱. در تلگرام به [@BotFather](https://t.me/BotFather) پیام بدهید
۲. دستور `/newbot` را بزنید و نام و یوزرنیم انتخاب کنید
۳. توکن را کپی کنید (چیزی شبیه `7123456789:AAH...`)

### ۲. آپلود روی گیت‌هاب

</div>

```bash
cd tg-video-dl-bot
git init
git add .
git commit -m "Telegram video direct link bot"
git branch -M main
git remote add origin https://github.com/USERNAME/tg-video-dl-bot.git
git push -u origin main
```

<div dir="rtl">

### ۳. ساخت سرویس در Railway
۱. وارد [railway.app](https://railway.app) شوید → **New Project**
۲. **Deploy from GitHub repo** → ریپازیتوری خود را انتخاب کنید
۳. Railway به‌صورت خودکار پایتون را تشخیص می‌دهد و بیلد می‌کند

### ۴. ساخت دامنهٔ عمومی (قبل از تنظیم متغیرها!)
در سرویس → تب **Settings** → بخش **Networking** → دکمهٔ **Generate Domain**
آدرسی مثل `my-bot-production.up.railway.app` می‌گیرید.

### ۵. تنظیم متغیرهای محیطی
در تب **Variables** این‌ها را اضافه کنید:

</div>

| Variable | Value |
|---|---|
| `BOT_TOKEN` | توکنی که از BotFather گرفتید |
| `BASE_URL` | `https://${{RAILWAY_PUBLIC_DOMAIN}}` |
| `SECRET_KEY` | یک رشتهٔ تصادفی بلند (پایین ببینید) |

<div dir="rtl">

> 💡 مقدار `${{RAILWAY_PUBLIC_DOMAIN}}` را دقیقاً با همین شکل بنویسید — Railway خودش آن را با دامنهٔ شما جایگزین می‌کند.

برای ساخت `SECRET_KEY`:

</div>

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

<div dir="rtl">

### ۶. تمام!
بعد از دیپلوی، ربات خودش وبهوک را ثبت می‌کند. در تلگرام `/start` را بزنید و یک ویدیو فوروارد کنید.

بررسی سلامت سرویس:

</div>

```bash
curl https://your-app.up.railway.app/health
# {"ok":true,"version":"1.0.0","mode":"webhook","link_mode":"signed"}
```

---

<div dir="rtl">

## 🔧 همهٔ متغیرهای محیطی

### الزامی

</div>

| متغیر | توضیح |
|---|---|
| `BOT_TOKEN` | توکن ربات از BotFather |
| `BASE_URL` | آدرس عمومی سرویس، مثلاً `https://${{RAILWAY_PUBLIC_DOMAIN}}` |
| `SECRET_KEY` | کلید تصادفی برای امضای لینک‌ها و وبهوک |

<div dir="rtl">

### اختیاری

</div>

| متغیر | پیش‌فرض | توضیح |
|---|---|---|
| `MODE` | `webhook` | `webhook` یا `polling` (برای تست محلی) |
| `BOT_LANG` | `fa` | `fa` یا `en` |
| `LINK_MODE` | `signed` | `signed` = بدون دیتابیس، `short` = لینک کوتاه با دیتابیس |
| `LINK_TTL_HOURS` | `0` | `0` یعنی لینک دائمی؛ عدد = ساعت اعتبار |
| `MAX_FILE_SIZE_MB` | `20` | سقف حجم مجاز |
| `RATE_LIMIT_PER_MINUTE` | `20` | حداکثر درخواست هر کاربر در دقیقه |
| `ADMIN_IDS` | – | آیدی عددی ادمین‌ها با کاما، برای `/stats` و `/broadcast` |
| `ALLOWED_USER_IDS` | – | اگر پر شود ربات خصوصی می‌شود |
| `REQUIRED_CHANNEL` | – | عضویت اجباری، مثل `@mychannel` (ربات باید ادمین کانال باشد) |
| `DATA_DIR` | `./data` | مسیر دیتابیس SQLite |
| `WEBHOOK_PATH` | خودکار | مسیر دلخواه وبهوک |
| `TELEGRAM_API_BASE` | `https://api.telegram.org` | برای سرور محلی Bot API |

<div dir="rtl">

> 🔎 آیدی عددی خودتان را از [@userinfobot](https://t.me/userinfobot) بگیرید.

---

## 🎛 حالت‌های لینک

### `signed` (پیش‌فرض، پیشنهادی)

</div>

```
https://your-app.up.railway.app/f/<token>/video.mp4
```

<div dir="rtl">

اطلاعات فایل داخل خودِ توکن (فشرده و امضاشده با HMAC) قرار دارد. یعنی:
- ✅ حتی اگر دیتابیس پاک شود، لینک‌های قدیمی کار می‌کنند
- ✅ نیازی به Volume روی Railway نیست
- ➖ لینک کمی بلند است

### `short`

</div>

```
https://your-app.up.railway.app/dl/a1b2c3d4/video.mp4
```

<div dir="rtl">

لینک کوتاه و شمارش دانلود دارد، ولی به دیتابیس وابسته است. اگر این حالت را انتخاب می‌کنید، حتماً روی Railway یک **Volume** به مسیر `/data` وصل کنید و `DATA_DIR=/data` بگذارید، وگرنه با هر دیپلوی لینک‌ها از بین می‌روند.

---

## 💬 دستورهای ربات

</div>

| دستور | کاربرد |
|---|---|
| `/start` | شروع و راهنمای سریع |
| `/help` | راهنمای کامل |
| `/myfiles` | ۱۰ فایل آخر شما |
| `/about` | دربارهٔ ربات |
| `/stats` | آمار (فقط ادمین) |
| `/broadcast متن` | پیام همگانی (فقط ادمین) |

<div dir="rtl">

## 🌐 مسیرهای وب

</div>

| مسیر | کاربرد |
|---|---|
| `GET /` | صفحهٔ اصلی |
| `GET /health` | health check برای Railway |
| `GET|HEAD /f/{token}/{filename}` | دانلود مستقیم (حالت signed) |
| `GET /p/{token}` | صفحهٔ دانلود (حالت signed) |
| `GET|HEAD /dl/{slug}/{filename}` | دانلود مستقیم (حالت short) |
| `GET /d/{slug}` | صفحهٔ دانلود (حالت short) |
| `POST /webhook/{hash}` | وبهوک تلگرام (محافظت‌شده) |

<div dir="rtl">

افزودن `?inline=1` به لینک دانلود باعث پخش در مرورگر می‌شود به‌جای دانلود.

---

## 💻 اجرای محلی

</div>

```bash
git clone https://github.com/USERNAME/tg-video-dl-bot.git
cd tg-video-dl-bot

python -m venv .venv
source .venv/bin/activate        # ویندوز: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # سپس .env را ویرایش کنید
```

<div dir="rtl">

برای تست محلی بدون دامنهٔ عمومی، در `.env` بگذارید `MODE=polling`:

</div>

```bash
python -m app.main
```

<div dir="rtl">

> در حالت `polling` لینک‌های دانلود فقط روی `localhost` کار می‌کنند. برای دسترسی از بیرون از [ngrok](https://ngrok.com) استفاده کنید و `BASE_URL` را روی آدرس ngrok بگذارید.

### اجرا با Docker

</div>

```bash
cp .env.example .env    # مقادیر را پر کنید
docker compose up -d
```

<div dir="rtl">

### اجرای تست‌ها

</div>

```bash
pip install pytest
BOT_TOKEN=123:TEST SECRET_KEY=test BASE_URL=https://example.com pytest -q
```

---

<div dir="rtl">

## 📦 فایل‌های بزرگ‌تر از ۲۰ مگابایت

برای عبور از محدودیت، یک [سرور محلی Telegram Bot API](https://github.com/tdlib/telegram-bot-api) اجرا کنید:

۱. از [my.telegram.org](https://my.telegram.org) مقادیر `api_id` و `api_hash` را بگیرید
۲. سرور را اجرا کنید (مثلاً با ایمیج `aiogram/telegram-bot-api`)
۳. در متغیرها بگذارید:

</div>

```env
TELEGRAM_API_BASE=http://your-bot-api-server:8081
MAX_FILE_SIZE_MB=2000
```

<div dir="rtl">

کد بقیهٔ کارها را خودش انجام می‌دهد (هم aiogram و هم لایهٔ دانلود از این آدرس استفاده می‌کنند).

---

## 🗂 ساختار پروژه

</div>

```
tg-video-dl-bot/
├── app/
│   ├── main.py       # نقطهٔ ورود: FastAPI + ربات در یک پروسه
│   ├── bot.py        # هندلرهای aiogram
│   ├── web.py        # مسیرهای دانلود، صفحهٔ دانلود، وبهوک
│   ├── telegram.py   # کلاینت Bot API + استریم فایل
│   ├── tokens.py     # ساخت/اعتبارسنجی توکن امضاشده
│   ├── db.py         # SQLite (آمار و لینک کوتاه)
│   ├── texts.py      # متن‌های فارسی/انگلیسی
│   ├── utils.py      # ابزارها و محدودکنندهٔ نرخ
│   └── config.py     # تنظیمات از env
├── tests/            # ۱۷ تست
├── requirements.txt
├── Procfile          # برای Railway/Heroku
├── railway.json      # تنظیمات Railway + healthcheck
├── nixpacks.toml
├── Dockerfile
└── docker-compose.yml
```

<div dir="rtl">

## 🩺 رفع اشکال

| مشکل | راه‌حل |
|---|---|
| `Invalid value for '--port': '$PORT'` | **Start Command را خالی کنید** یا روی `python -m app.main` بگذارید. توضیح کامل پایین‌تر ↓ |
| ربات جواب نمی‌دهد | لاگ Railway را ببینید؛ معمولاً `BASE_URL` اشتباه است یا دامنه ساخته نشده |
| لینک ۴۰۴ می‌دهد | فایل روی سرورهای تلگرام حذف شده، یا `SECRET_KEY` تغییر کرده (لینک‌های قدیمی باطل می‌شوند) |
| «فایل خیلی بزرگ است» | محدودیت ۲۰ مگابایتی Bot API — بخش فایل‌های بزرگ را ببینید |
| بعد از دیپلوی لینک‌های `short` خراب شد | Volume وصل نشده؛ یا `LINK_MODE=signed` بگذارید |
| در لاگ `Unauthorized` می‌بینید | `BOT_TOKEN` غلط است |

### ❗️ خطای `Invalid value for '--port': '$PORT' is not a valid integer`

**علت:** Railway دستور `Start Command` را بدون شل اجرا می‌کند. برای همین `$PORT` هیچ‌وقت باز نمی‌شود و رشتهٔ خامِ `$PORT` به uvicorn می‌رسد.

**راه‌حل:** در این پروژه دستور اجرا `python -m app.main` است و پورت را **خودِ پایتون** از متغیر محیطی می‌خواند، پس این خطا رخ نمی‌دهد.

اگر باز هم این خطا را می‌بینید یعنی Railway هنوز دستور قدیمی را نگه داشته است:

۱. آخرین نسخه را push کنید:

</div>

```bash
git add -A && git commit -m "fix: port handling" && git push
```

<div dir="rtl">

۲. در Railway → سرویس → **Settings** → **Deploy** → فیلد **Custom Start Command** را پیدا کنید.
اگر داخلش چیزی شبیه `uvicorn ... --port $PORT` نوشته شده، **آن را کاملاً پاک کنید** (تا از `railway.json` خوانده شود) یا دقیقاً بگذارید:

</div>

```
python -m app.main
```

<div dir="rtl">

۳. **Redeploy** بزنید.

> ✅ اگر روزی خواستید حتماً از uvicorn مستقیم استفاده کنید، حتماً با شل اجرا کنید:
> `sh -c "uvicorn app.main:app --host 0.0.0.0 --port $PORT"`

## 📄 لایسنس

MIT

</div>
