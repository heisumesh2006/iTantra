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


def initialize() -> None:
    with connection() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS schema_version(version INTEGER PRIMARY KEY);
        INSERT OR IGNORE INTO schema_version VALUES(1);
        CREATE TABLE IF NOT EXISTS media(id TEXT PRIMARY KEY, created_at TEXT, path TEXT, metadata TEXT);
        CREATE TABLE IF NOT EXISTS transmissions(id TEXT PRIMARY KEY, created_at TEXT, status TEXT,
            config TEXT, result TEXT, error TEXT, stages TEXT);
        CREATE TABLE IF NOT EXISTS experiments(id TEXT PRIMARY KEY, created_at TEXT, status TEXT,
            config TEXT, result TEXT, error TEXT, stages TEXT);
        CREATE TABLE IF NOT EXISTS experiment_results(id TEXT PRIMARY KEY, experiment_id TEXT, result TEXT);
        CREATE TABLE IF NOT EXISTS model_metadata(id TEXT PRIMARY KEY, metadata TEXT);
        CREATE TABLE IF NOT EXISTS comparisons(id TEXT PRIMARY KEY, created_at TEXT, metadata TEXT);
        """)
        for table in ("transmissions", "experiments"):
            db.execute(
                f"UPDATE {table} SET status='failed', error='Server restarted during processing' "
                "WHERE status IN ('queued','running')"
            )
