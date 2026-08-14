import { NextRequest } from "next/server";
import { db } from "@/db";
import { videos } from "@/db/schema";
import { eq } from "drizzle-orm";
import fs from "fs/promises";

export const dynamic = "force-dynamic";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ token: string }> }
) {
  try {
    const { token } = await params;

    const result = await db
      .select()
      .from(videos)
      .where(eq(videos.downloadToken, token))
      .limit(1);

    if (result.length === 0) {
      return new Response("❌ فایل یافت نشد", { status: 404 });
    }

    const video = result[0];

    if (!video.localPath) {
      return new Response("❌ فایل در دسترس نیست", { status: 404 });
    }

    // Check if file exists on disk
    try {
      await fs.access(video.localPath);
    } catch {
      return new Response("❌ فایل از سرور حذف شده است", { status: 404 });
    }

    const fileBuffer = await fs.readFile(video.localPath);
    const fileName = video.fileName || "video.mp4";
    const mimeType = video.mimeType || "video/mp4";

    return new Response(fileBuffer, {
      headers: {
        "Content-Type": mimeType,
        "Content-Disposition": `attachment; filename="${encodeURIComponent(fileName)}"`,
        "Content-Length": String(fileBuffer.length),
        "Cache-Control": "public, max-age=31536000",
      },
    });
  } catch (error) {
    console.error("Download error:", error);
    return new Response("❌ خطای سرور", { status: 500 });
  }
}
