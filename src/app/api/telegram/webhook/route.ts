import { NextRequest } from "next/server";
import { db } from "@/db";
import { videos } from "@/db/schema";
import { sendMessage, getFile, getFileUrl } from "@/lib/telegram";
import { v4 as uuidv4 } from "uuid";
import { eq } from "drizzle-orm";
import fs from "fs/promises";
import path from "path";

export const dynamic = "force-dynamic";

const UPLOAD_DIR = path.join(process.cwd(), "public", "uploads");

async function ensureUploadDir() {
  try {
    await fs.mkdir(UPLOAD_DIR, { recursive: true });
  } catch {
    // directory exists
  }
}

async function downloadAndSaveFile(fileUrl: string, fileName: string): Promise<string> {
  await ensureUploadDir();
  const res = await fetch(fileUrl);
  if (!res.ok) throw new Error("Failed to download file from Telegram");
  const buffer = Buffer.from(await res.arrayBuffer());
  const filePath = path.join(UPLOAD_DIR, fileName);
  await fs.writeFile(filePath, buffer);
  return filePath;
}

function getBaseUrl(): string {
  if (process.env.BASE_URL) return process.env.BASE_URL;
  if (process.env.RAILWAY_PUBLIC_DOMAIN) return `https://${process.env.RAILWAY_PUBLIC_DOMAIN}`;
  if (process.env.VERCEL_URL) return `https://${process.env.VERCEL_URL}`;
  return "http://localhost:3000";
}

function formatFileSize(bytes: number | null | undefined): string {
  if (!bytes) return "نامشخص";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDuration(seconds: number | null | undefined): string {
  if (!seconds) return "نامشخص";
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function handleVideo(message: any) {
  const chatId = message.chat.id;
  const video = message.video || message.document;

  if (!video) return;

  const isDocument = !message.video && message.document;
  const isVideoDocument = isDocument && video.mime_type?.startsWith("video/");

  if (isDocument && !isVideoDocument) {
    await sendMessage(chatId, "⚠️ لطفاً فقط ویدیو ارسال کنید.");
    return;
  }

  try {
    await sendMessage(chatId, "⏳ در حال پردازش ویدیو... لطفاً صبر کنید.");

    // Check if already processed
    const existing = await db.select().from(videos).where(eq(videos.fileId, video.file_id)).limit(1);
    if (existing.length > 0) {
      const baseUrl = getBaseUrl();
      const downloadUrl = `${baseUrl}/api/download/${existing[0].downloadToken}`;
      await sendMessage(
        chatId,
        `✅ این ویدیو قبلاً پردازش شده!\n\n` +
        `🔗 <b>لینک دانلود مستقیم:</b>\n<code>${downloadUrl}</code>\n\n` +
        `روی لینک بزنید یا کپی کنید.`
      );
      return;
    }

    // Get file info from Telegram
    const fileInfo = await getFile(video.file_id);
    if (!fileInfo.ok) {
      await sendMessage(chatId, "❌ خطا در دریافت اطلاعات فایل. ممکنه حجم ویدیو بیشتر از ۲۰ مگابایت باشه.");
      return;
    }

    const downloadToken = uuidv4();
    const ext = video.file_name
      ? path.extname(video.file_name)
      : video.mime_type
        ? `.${video.mime_type.split("/")[1]}`
        : ".mp4";
    const savedFileName = `${downloadToken}${ext}`;

    // Download file
    const telegramFileUrl = getFileUrl(fileInfo.result.file_path);
    const localPath = await downloadAndSaveFile(telegramFileUrl, savedFileName);

    // Save to database
    await db.insert(videos).values({
      fileId: video.file_id,
      uniqueId: video.file_unique_id,
      fileName: video.file_name || `video${ext}`,
      fileSize: video.file_size || null,
      mimeType: video.mime_type || "video/mp4",
      duration: video.duration || null,
      width: video.width || null,
      height: video.height || null,
      downloadToken,
      telegramUserId: String(message.from?.id || ""),
      telegramUsername: message.from?.username || null,
      caption: message.caption || null,
      localPath,
    });

    const baseUrl = getBaseUrl();
    const downloadUrl = `${baseUrl}/api/download/${downloadToken}`;

    const responseText =
      `✅ <b>ویدیو با موفقیت پردازش شد!</b>\n\n` +
      `📁 <b>نام فایل:</b> ${video.file_name || "video" + ext}\n` +
      `📦 <b>حجم:</b> ${formatFileSize(video.file_size)}\n` +
      `⏱ <b>مدت:</b> ${formatDuration(video.duration)}\n` +
      (video.width ? `📐 <b>ابعاد:</b> ${video.width}x${video.height}\n` : "") +
      `\n🔗 <b>لینک دانلود مستقیم:</b>\n<code>${downloadUrl}</code>\n\n` +
      `💡 این لینک دائمی است و هر زمان می‌توانید از آن استفاده کنید.`;

    await sendMessage(chatId, responseText);
  } catch (error) {
    console.error("Error processing video:", error);
    await sendMessage(chatId, "❌ خطا در پردازش ویدیو. لطفاً دوباره تلاش کنید.");
  }
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function handleStart(message: any) {
  const chatId = message.chat.id;
  const name = message.from?.first_name || "کاربر";

  const welcomeText =
    `سلام ${name}! 👋\n\n` +
    `🤖 <b>به ربات دانلود ویدیو خوش آمدید!</b>\n\n` +
    `📌 <b>نحوه استفاده:</b>\n` +
    `1️⃣ یک ویدیو رو به من فوروارد کنید یا مستقیم ارسال کنید\n` +
    `2️⃣ من ویدیو رو پردازش می‌کنم\n` +
    `3️⃣ لینک دانلود مستقیم رو دریافت می‌کنید\n\n` +
    `⚠️ <b>محدودیت:</b> حداکثر حجم ویدیو ۲۰ مگابایت (محدودیت API تلگرام)\n\n` +
    `📋 <b>دستورات:</b>\n` +
    `/start - شروع مجدد\n` +
    `/help - راهنما\n` +
    `/stats - آمار شما`;

  await sendMessage(chatId, welcomeText);
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function handleHelp(message: any) {
  const chatId = message.chat.id;

  const helpText =
    `📖 <b>راهنمای ربات</b>\n\n` +
    `🎬 <b>ارسال ویدیو:</b>\n` +
    `• ویدیو رو مستقیم به ربات ارسال کنید\n` +
    `• یا از کانال/گروه فوروارد کنید\n` +
    `• ویدیو به صورت فایل هم قابل قبوله\n\n` +
    `🔗 <b>لینک دانلود:</b>\n` +
    `• لینک دائمی است\n` +
    `• بدون نیاز به VPN قابل دانلوده\n` +
    `• قابل اشتراک‌گذاری با دیگران\n\n` +
    `⚠️ <b>نکات مهم:</b>\n` +
    `• حداکثر حجم: ۲۰ مگابایت\n` +
    `• فرمت‌های پشتیبانی: MP4, MKV, AVI, MOV\n`;

  await sendMessage(chatId, helpText);
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function handleStats(message: any) {
  const chatId = message.chat.id;
  const userId = String(message.from?.id || "");

  const userVideos = await db
    .select()
    .from(videos)
    .where(eq(videos.telegramUserId, userId));

  const totalSize = userVideos.reduce((sum, v) => sum + (v.fileSize || 0), 0);

  const statsText =
    `📊 <b>آمار شما:</b>\n\n` +
    `🎬 تعداد ویدیوها: ${userVideos.length}\n` +
    `💾 حجم کل: ${formatFileSize(totalSize)}\n`;

  await sendMessage(chatId, statsText);
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const message = body.message;

    if (!message) {
      return Response.json({ ok: true });
    }

    // Handle commands
    if (message.text) {
      const command = message.text.split(" ")[0].split("@")[0];
      switch (command) {
        case "/start":
          await handleStart(message);
          return Response.json({ ok: true });
        case "/help":
          await handleHelp(message);
          return Response.json({ ok: true });
        case "/stats":
          await handleStats(message);
          return Response.json({ ok: true });
      }
    }

    // Handle video
    if (message.video || (message.document && message.document.mime_type?.startsWith("video/"))) {
      await handleVideo(message);
      return Response.json({ ok: true });
    }

    // Handle other messages
    if (!message.video && !message.document) {
      await sendMessage(
        message.chat.id,
        "🎬 لطفاً یک ویدیو ارسال یا فوروارد کنید تا لینک دانلود مستقیم دریافت کنید.\n\n/help - راهنما"
      );
    }

    return Response.json({ ok: true });
  } catch (error) {
    console.error("Webhook error:", error);
    return Response.json({ ok: true });
  }
}

export async function GET() {
  return Response.json({ status: "Telegram webhook is active" });
}
