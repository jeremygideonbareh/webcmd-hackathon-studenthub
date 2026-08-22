"""
SQLite ledger for Atlas — reactions, preference weights, digest history.

Usage:
    from delivery.database import Database
    db = Database()
    db.log_reaction("msg_1", "job", "internshala_12345", "👍")
    weights = db.get_all_weights()
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS reactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT NOT NULL,
    item_type TEXT NOT NULL,
    item_id TEXT NOT NULL,
    reaction TEXT NOT NULL,
    reacted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS preference_weights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL UNIQUE,
    weight REAL DEFAULT 1.0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS digest_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    digest_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


class Database:
    """SQLite CRUD wrapper for the Atlas preference ledger."""

    def __init__(self, db_path: str | Path = "atlas.db"):
        self.db_path = str(db_path)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    # --- reactions ---

    def log_reaction(self, message_id: str, item_type: str, item_id: str, reaction: str) -> int:
        cur = self._conn.execute(
            "INSERT INTO reactions (message_id, item_type, item_id, reaction) VALUES (?, ?, ?, ?)",
            (message_id, item_type, item_id, reaction),
        )
        self._conn.commit()
        return cur.lastrowid

    def get_reactions(self, limit: int = 100) -> list[dict]:
        rows = self._conn.execute(
            "SELECT * FROM reactions ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    # --- preference weights ---

    def get_weight(self, category: str) -> float:
        row = self._conn.execute(
            "SELECT weight FROM preference_weights WHERE category = ?", (category,)
        ).fetchone()
        return row["weight"] if row else 1.0

    def update_weight(self, category: str, weight: float) -> None:
        self._conn.execute(
            """
            INSERT INTO preference_weights (category, weight) VALUES (?, ?)
            ON CONFLICT(category) DO UPDATE SET weight = excluded.weight,
                updated_at = CURRENT_TIMESTAMP
            """,
            (category, weight),
        )
        self._conn.commit()

    def get_all_weights(self) -> dict[str, float]:
        rows = self._conn.execute("SELECT category, weight FROM preference_weights").fetchall()
        return {r["category"]: r["weight"] for r in rows}

    # --- digest history ---

    def log_digest(self, digest_type: str, payload_json: str) -> int:
        cur = self._conn.execute(
            "INSERT INTO digest_history (digest_type, payload_json) VALUES (?, ?)",
            (digest_type, payload_json),
        )
        self._conn.commit()
        return cur.lastrowid

    def get_digest_history(self, limit: int = 20) -> list[dict]:
        rows = self._conn.execute(
            "SELECT * FROM digest_history ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_digest_item(self, item_id: str) -> dict | None:
        """Search digest history payloads for an item by id and return its metadata."""
        rows = self._conn.execute(
            "SELECT payload_json FROM digest_history ORDER BY id DESC LIMIT 50"
        ).fetchall()
        for row in rows:
            try:
                payload = json.loads(row["payload_json"])
            except (json.JSONDecodeError, TypeError):
                continue
            for section in ("jobs", "housing"):
                for item in payload.get(section, []):
                    if str(item.get("id")) == str(item_id):
                        return item
        return None

    # --- helpers ---

    def get_tables(self) -> set[str]:
        rows = self._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        return {r["name"] for r in rows}

    def close(self) -> None:
        self._conn.close()