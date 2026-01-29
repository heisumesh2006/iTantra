import json
import unicodedata
import zlib
from app.core.errors import ApplicationError


def normalize(text: str) -> str:
    return unicodedata.normalize("NFC", text).strip()


def encode(text: str, language: str) -> bytes:
    text = normalize(text)
    if not text:
        raise ApplicationError("Transcript is empty")
    raw = json.dumps({"text": text, "language": language}, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )
    compressed = zlib.compress(raw)
    return (b"SC1Z" + compressed) if len(compressed) < len(raw) else (b"SC1U" + raw)
