import struct
import zlib
from dataclasses import dataclass
from uuid import UUID
from app.core.errors import ApplicationError

HEADER = struct.Struct(">2sB16sHHBBH")
CRC = struct.Struct(">I")
MAGIC = b"IT"
VERSION = 1
MAX_PAYLOAD = 1024
MAX_PACKETS = 4096
MODES = {"conventional": 1, "neural": 2, "semantic": 3}
LANGUAGES = {"en": 1, "hi": 2, "kn": 3, "ta": 4, "te": 5, "ml": 6}


@dataclass(frozen=True)
class Packet:
    session: UUID
    sequence: int
    total: int
    mode: int
    language: int
    payload: bytes

    def serialize(self) -> bytes:
        if not (0 <= self.sequence < self.total <= MAX_PACKETS) or not (0 < len(self.payload) <= MAX_PAYLOAD):
            raise ApplicationError("Invalid packet bounds")
        if self.mode not in MODES.values() or self.language not in LANGUAGES.values():
            raise ApplicationError("Unknown mode or language")
        framed = (
            HEADER.pack(
                MAGIC,
                VERSION,
                self.session.bytes,
                self.sequence,
                self.total,
                self.mode,
                self.language,
                len(self.payload),
            )
            + self.payload
        )
        return framed + CRC.pack(zlib.crc32(framed))
