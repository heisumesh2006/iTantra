import json
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4
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


def register_media(path, metadata: dict) -> dict:
    identifier = str(uuid4())
    entry = {"id": identifier, "created_at": now(), **metadata, "url": f"/api/v1/media/{identifier}"}
    with connection() as db:
        db.execute(
            "INSERT INTO media VALUES(?,?,?,?)",
            (identifier, entry["created_at"], str(path), json.dumps(entry)),
        )
    return entry


def get_media(identifier: str):
    with connection() as db:
        row = db.execute("SELECT * FROM media WHERE id=?", (identifier,)).fetchone()
    return dict(row) if row else None


def media_entries():
    with connection() as db:
        return [dict(row) for row in db.execute("SELECT * FROM media")]


def remove_media(identifier: str):
    with connection() as db:
        db.execute("DELETE FROM media WHERE id=?", (identifier,))


def create_job(table: str, config: dict) -> dict:
    assert table in ("transmissions", "experiments")
    job = {
        "id": str(uuid4()),
        "created_at": now(),
        "status": "queued",
        "config": config,
        "result": None,
        "error": None,
        "stages": [],
    }
    with connection() as db:
        db.execute(
            f"INSERT INTO {table} VALUES(?,?,?,?,?,?,?)",
            (job["id"], job["created_at"], job["status"], json.dumps(config), None, None, "[]"),
        )
    return job
