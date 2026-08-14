import { pgTable, text, timestamp, integer, serial } from "drizzle-orm/pg-core";

export const videos = pgTable("videos", {
  id: serial("id").primaryKey(),
  fileId: text("file_id").notNull(),
  uniqueId: text("unique_id").notNull().unique(),
  fileName: text("file_name"),
  fileSize: integer("file_size"),
  mimeType: text("mime_type"),
  duration: integer("duration"),
  width: integer("width"),
  height: integer("height"),
  downloadToken: text("download_token").notNull().unique(),
  telegramUserId: text("telegram_user_id"),
  telegramUsername: text("telegram_username"),
  caption: text("caption"),
  localPath: text("local_path"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});
