import struct
from dataclasses import dataclass
from uuid import UUID

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
