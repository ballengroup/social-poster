"""Tiny SQLite log so a video is never sent to the same destination twice."""

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,
    destination TEXT NOT NULL,
    status TEXT NOT NULL,          -- 'done' | 'failed' | 'skipped'
    detail TEXT,
    caption TEXT,
    attempts INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (source, source_id, destination)
);
"""


class History:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.executescript(SCHEMA)

    def status(self, source: str, source_id: str, destination: str) -> str | None:
        row = self.conn.execute(
            "SELECT status FROM posts WHERE source=? AND source_id=? AND destination=?",
            (source, source_id, destination),
        ).fetchone()
        return row[0] if row else None

    def attempts(self, source: str, source_id: str, destination: str) -> int:
        row = self.conn.execute(
            "SELECT attempts FROM posts WHERE source=? AND source_id=? AND destination=?",
            (source, source_id, destination),
        ).fetchone()
        return row[0] if row else 0

    def record(self, source, source_id, destination, status, detail="", caption=""):
        self.conn.execute(
            """
            INSERT INTO posts (source, source_id, destination, status, detail, caption)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (source, source_id, destination) DO UPDATE SET
                status=excluded.status, detail=excluded.detail,
                attempts=posts.attempts + 1, updated_at=datetime('now')
            """,
            (source, source_id, destination, status, detail, caption),
        )
        self.conn.commit()

    def recent(self, limit: int = 25):
        return self.conn.execute(
            "SELECT updated_at, source, source_id, destination, status, detail "
            "FROM posts ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
