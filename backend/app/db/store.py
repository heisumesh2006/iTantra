import sqlite3
from datetime import datetime, timezone
from app.core.config import STORAGE

DB = STORAGE / "itantra.sqlite3"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connection():
    db = sqlite3.connect(DB, timeout=30)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    return db
