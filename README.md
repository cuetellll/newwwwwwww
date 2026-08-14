# 🤖 ربات دانلود ویدیو تلگرام

ویدیو به ربات فوروارد کنید، لینک دانلود مستقیم دریافت کنید!

![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?logo=typescript)

## ✨ قابلیت‌ها

- 🎬 دریافت ویدیو از تلگرام و تولید لینک دانلود مستقیم
- 📱 پشتیبانی از ویدیو و فایل‌های ویدیویی
- 🔗 لینک‌های دائمی و قابل اشتراک‌گذاری
- 📊 داشبورد مدیریت با آمار کامل
- 🚫 جلوگیری از پردازش تکراری

## 🚀 راه‌اندازی روی Railway

### 1. ساخت ربات تلگرام

1. به [@BotFather](https://t.me/BotFather) پیام بدید
2. دستور `/newbot` رو بزنید
3. نام و username ربات رو وارد کنید
4. **توکن** رو کپی کنید

### 2. دیپلوی روی Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

1. این ریپو رو Fork کنید
2. در Railway یک پروژه جدید بسازید
3. ریپوی گیت‌هاب رو متصل کنید
4. یک **PostgreSQL** به پروژه اضافه کنید
5. متغیرهای محیطی رو تنظیم کنید:

### 3. متغیرهای محیطی (Environment Variables)

| متغیر | توضیح | مثال |
|-------|-------|------|
| `DATABASE_URL` | آدرس دیتابیس (خودکار توسط Railway) | `postgresql://...` |
| `TELEGRAM_BOT_TOKEN` | توکن از BotFather | `123456:ABC-DEF...` |
| `BASE_URL` | آدرس اپلیکیشن | `https://your-app.railway.app` |

### 4. فعال‌سازی Webhook

بعد از دیپلوی:

1. به داشبورد وب برید: `https://your-app.railway.app`
2. در قسمت تنظیمات، آدرس webhook رو وارد کنید:
   ```
   https://your-app.railway.app/api/telegram/webhook
   ```
3. دکمه "فعال‌سازی" رو بزنید

## 📱 دستورات ربات

| دستور | توضیح |
|-------|-------|
| `/start` | شروع و خوش‌آمدگویی |
| `/help` | راهنمای استفاده |
| `/stats` | آمار ویدیوهای شما |

## 🎬 نحوه استفاده

1. ویدیو رو به ربات فوروارد کنید
2. منتظر پردازش بمونید
3. لینک دانلود مستقیم رو دریافت کنید!

## ⚠️ محدودیت‌ها

- حداکثر حجم ویدیو: **20 مگابایت** (محدودیت API تلگرام)
- فرمت‌های پشتیبانی شده: MP4, MKV, AVI, MOV, WebM

## 🛠️ تکنولوژی‌ها

- **Next.js 16** - فریمورک React
- **PostgreSQL** - دیتابیس
- **Drizzle ORM** - مدیریت دیتابیس
- **Tailwind CSS** - استایل‌دهی
- **TypeScript** - تایپ‌سیفتی

## 📁 ساختار پروژه

```
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   ├── telegram/
│   │   │   │   ├── webhook/     # Webhook اصلی
│   │   │   │   ├── setup/       # تنظیم Webhook
│   │   │   │   └── stats/       # آمار
│   │   │   ├── download/[token]/ # دانلود فایل
│   │   │   └── health/          # Health check
│   │   └── page.tsx             # داشبورد
│   ├── db/
│   │   ├── index.ts             # اتصال دیتابیس
│   │   └── schema.ts            # مدل‌ها
│   └── lib/
│       └── telegram.ts          # توابع تلگرام
└── public/
    └── uploads/                 # فایل‌های دانلود شده
```

## 🔧 توسعه لوکال

```bash
# نصب dependencies
npm install

# ساخت فایل .env
cp .env.example .env

# اجرای دیتابیس (با Docker)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=app_db postgres:15

# Push کردن schema
npx drizzle-kit push

# اجرای سرور توسعه
npm run dev
```

## 📄 لایسنس

MIT License

---

ساخته شده با ❤️
