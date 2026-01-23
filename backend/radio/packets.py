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

    @classmethod
    def parse(cls, raw: bytes):
        if len(raw) < HEADER.size + CRC.size:
            raise ApplicationError("Truncated packet")
        magic, version, session, seq, total, mode, lang, length = HEADER.unpack(raw[: HEADER.size])
        if magic != MAGIC or version != VERSION or len(raw) != HEADER.size + length + CRC.size:
            raise ApplicationError("Packet header or length invalid")
        if zlib.crc32(raw[:-4]) != CRC.unpack(raw[-4:])[0]:
            raise ApplicationError("CRC mismatch", "integrity_failure")
        packet = cls(UUID(bytes=session), seq, total, mode, lang, raw[HEADER.size : -4])
        packet.serialize()  # validate all bounds and identifiers
        return packet


def segment(payload: bytes, session: UUID, mode: str, language: str, packet_size: int) -> list[Packet]:
    if not payload or not 32 <= packet_size <= MAX_PAYLOAD:
        raise ApplicationError("Empty payload or invalid packet size")
    total = (len(payload) + packet_size - 1) // packet_size
    if total > MAX_PACKETS:
        raise ApplicationError("Payload exceeds packet count bound")
    return [
        Packet(
            session,
            i,
            total,
            MODES[mode],
            LANGUAGES[language],
            payload[i * packet_size : (i + 1) * packet_size],
        )
        for i in range(total)
    ]


def reassemble(packets: list[Packet]) -> bytes:
    if not packets:
        raise ApplicationError("No intact packets recovered", "recovery_failure")
    first = packets[0]
    if len(packets) != first.total or len({p.sequence for p in packets}) != first.total:
        raise ApplicationError(
            "Missing or duplicate packets; receiver cannot reconstruct payload", "recovery_failure"
        )
    if any(
        (p.session, p.total, p.mode, p.language) != (first.session, first.total, first.mode, first.language)
        for p in packets
    ):
        raise ApplicationError("Inconsistent packet session metadata")
    return b"".join(p.payload for p in sorted(packets, key=lambda p: p.sequence))
