"""Migration runner.

Add a new migration: create NNN_description.py with an up(conn) function.
Runner discovers by globbing this directory. Never modify a shipped migration.
"""

import sqlite3
from importlib import import_module
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent


def migrate(conn: sqlite3.Connection) -> int:
    """Run pending migrations. Returns count applied."""
    conn.execute("CREATE TABLE IF NOT EXISTS _migrations (name TEXT PRIMARY KEY)")
    conn.commit()

    applied = {row[0] for row in conn.execute("SELECT name FROM _migrations").fetchall()}
    count = 0

    for py_file in sorted(MIGRATIONS_DIR.glob("[0-9]*.py")):
        name = py_file.stem
        if name in applied:
            continue
        mod = import_module(f"ccmeter.migrations.{name}")
        mod.up(conn)
        conn.execute("INSERT INTO _migrations (name) VALUES (?)", (name,))
        conn.commit()
        count += 1

    return count
