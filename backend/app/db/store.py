from datetime import datetime, timezone
from app.core.config import STORAGE

DB = STORAGE / "itantra.sqlite3"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()
