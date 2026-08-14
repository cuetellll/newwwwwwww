"""لایهٔ دیتابیس (SQLite) برای آمار، لینک‌های کوتاه و شمارش دانلود.

اگر LINK_MODE=signed باشد دیتابیس فقط برای آمار استفاده می‌شود و
حذف شدنش هم لینک‌ها را خراب نمی‌کند.
"""

from __future__ import annotations

import time
from typing import Any

import aiosqlite

from .config import settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id     INTEGER PRIMARY KEY,
    username    TEXT,
    first_name  TEXT,
    lang        TEXT,
    created_at  INTEGER,
    last_seen   INTEGER,
    files_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS files (
    slug        TEXT PRIMARY KEY,
    file_id     TEXT NOT NULL,
    file_name   TEXT,
    file_size   INTEGER,
    mime        TEXT,
    user_id     INTEGER,
    created_at  INTEGER,
    expires_at  INTEGER DEFAULT 0,
    downloads   INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_files_user ON files(user_id);
CREATE INDEX IF NOT EXISTS idx_files_created ON files(created_at);
"""


class Database:
    def __init__(self, path: str | None = None) -> None:
        self.path = path or settings.db_path
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA journal_mode=WAL;")
        await self._conn.executescript(_SCHEMA)
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    @property
    def is_connected(self) -> bool:
        return self._conn is not None

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("دیتابیس متصل نیست؛ ابتدا connect() را صدا بزنید")
        return self._conn

    # ---------------------------------------------------------- users
    async def upsert_user(
        self,
        user_id: int,
        username: str | None = None,
        first_name: str | None = None,
        lang: str | None = None,
    ) -> None:
        now = int(time.time())
        await self.conn.execute(
            """
            INSERT INTO users (user_id, username, first_name, lang, created_at, last_seen)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                first_name=excluded.first_name,
                last_seen=excluded.last_seen
            """,
            (user_id, username, first_name, lang, now, now),
        )
        await self.conn.commit()

    async def all_user_ids(self) -> list[int]:
        cur = await self.conn.execute("SELECT user_id FROM users")
        return [r[0] for r in await cur.fetchall()]

    # ---------------------------------------------------------- files
    async def save_file(
        self,
        slug: str,
        file_id: str,
        file_name: str,
        file_size: int,
        mime: str,
        user_id: int,
        expires_at: int = 0,
    ) -> None:
        await self.conn.execute(
            """
            INSERT OR REPLACE INTO files
                (slug, file_id, file_name, file_size, mime, user_id, created_at, expires_at,
                 downloads)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?,
                    COALESCE((SELECT downloads FROM files WHERE slug = ?), 0))
            """,
            (slug, file_id, file_name, file_size, mime, user_id,
             int(time.time()), expires_at, slug),
        )
        await self.conn.execute(
            "UPDATE users SET files_count = files_count + 1 WHERE user_id = ?",
            (user_id,),
        )
        await self.conn.commit()

    async def get_file(self, slug: str) -> dict[str, Any] | None:
        if not self.is_connected:
            return None
        cur = await self.conn.execute("SELECT * FROM files WHERE slug = ?", (slug,))
        row = await cur.fetchone()
        return dict(row) if row else None

    async def bump_download(self, slug: str) -> None:
        await self.conn.execute(
            "UPDATE files SET downloads = downloads + 1 WHERE slug = ?", (slug,)
        )
        await self.conn.commit()

    async def user_files(self, user_id: int, limit: int = 10) -> list[dict[str, Any]]:
        cur = await self.conn.execute(
            "SELECT * FROM files WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        )
        return [dict(r) for r in await cur.fetchall()]

    # ---------------------------------------------------------- stats
    async def stats(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for key, sql in {
            "users": "SELECT COUNT(*) FROM users",
            "files": "SELECT COUNT(*) FROM files",
            "downloads": "SELECT COALESCE(SUM(downloads),0) FROM files",
            "bytes": "SELECT COALESCE(SUM(file_size),0) FROM files",
            "today_users": (
                "SELECT COUNT(*) FROM users WHERE last_seen > strftime('%s','now','-1 day')"
            ),
            "today_files": (
                "SELECT COUNT(*) FROM files WHERE created_at > strftime('%s','now','-1 day')"
            ),
        }.items():
            cur = await self.conn.execute(sql)
            row = await cur.fetchone()
            out[key] = int(row[0] or 0)
        return out


db = Database()
