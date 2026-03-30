"""Track derived budget over time for trend detection."""

import sqlite3


def up(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS budget_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ts          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
            bucket      TEXT NOT NULL,
            budget      REAL NOT NULL,
            base_budget REAL NOT NULL,
            multiplier  INTEGER NOT NULL DEFAULT 1,
            ticks       INTEGER NOT NULL,
            rate_tier   TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_budget_bucket_ts ON budget_history(bucket, ts);
    """)
