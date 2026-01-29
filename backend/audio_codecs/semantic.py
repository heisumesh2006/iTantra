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


def decode(payload: bytes) -> dict:
    if payload[:4] == b"SC1Z":
        decompressor = zlib.decompressobj()
        raw = decompressor.decompress(payload[4:], 32769)
        if (
            len(raw) > 32768
            or decompressor.unconsumed_tail
            or not decompressor.eof
            or decompressor.unused_data
        ):
            raise ApplicationError("Semantic decompression bound or stream integrity failure")
    elif payload[:4] == b"SC1U":
        raw = payload[4:]
    else:
        raise ApplicationError("Invalid semantic envelope")
    try:
        entry = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeError) as error:
        raise ApplicationError("Invalid recovered Unicode text") from error
    if set(entry) != {"text", "language"} or not isinstance(entry["text"], str) or len(entry["text"]) > 4000:
        raise ApplicationError("Semantic payload schema invalid")
    return entry
