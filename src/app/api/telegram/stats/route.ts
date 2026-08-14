import { db } from "@/db";
import { videos } from "@/db/schema";
import { sql } from "drizzle-orm";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const totalVideos = await db.select({ count: sql<number>`count(*)` }).from(videos);
    const totalSize = await db
      .select({ total: sql<number>`coalesce(sum(file_size), 0)` })
      .from(videos);
    const recentVideos = await db
      .select()
      .from(videos)
      .orderBy(sql`created_at desc`)
      .limit(10);

    return Response.json({
      totalVideos: Number(totalVideos[0].count),
      totalSize: Number(totalSize[0].total),
      recentVideos: recentVideos.map((v) => ({
        id: v.id,
        fileName: v.fileName,
        fileSize: v.fileSize,
        duration: v.duration,
        username: v.telegramUsername,
        createdAt: v.createdAt,
      })),
    });
  } catch (error) {
    console.error("Stats error:", error);
    return Response.json({ error: "Failed to get stats" }, { status: 500 });
  }
}
