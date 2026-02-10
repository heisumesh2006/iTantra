from uuid import uuid4
import numpy as np
import pytest
from app.core.errors import ApplicationError
from app.schemas.requests import ChannelConfig
from radio.packets import Packet, segment
from radio.modulation import modulate, demodulate
from radio.channel import transport
from audio_codecs import semantic


@pytest.mark.parametrize("modulation", ["BPSK", "QPSK"])
@pytest.mark.parametrize("size", [1, 7, 8, 10001])
def test_noiseless_modulation(modulation, size):
    bits = np.random.default_rng(7).integers(0, 2, size, dtype=np.uint8)
    symbols, padding = modulate(bits, modulation)
    assert np.allclose(np.abs(symbols), 1)
    np.testing.assert_array_equal(bits, demodulate(symbols, modulation, padding))


@pytest.mark.parametrize(
    "language,text",
    [
        ("hi", "नमस्ते दुनिया"),
        ("kn", "ನಮಸ್ಕಾರ ಜಗತ್ತು"),
        ("ta", "வணக்கம் உலகம்"),
        ("te", "నమస్తే ప్రపంచం"),
        ("ml", "നമസ്കാരം ലോകം"),
        ("en", "A café in the world"),
    ],
)
def test_unicode_transport(language, text):
    payload = semantic.encode(text * 30, language)
    result = transport(payload, uuid4(), "semantic", language, ChannelConfig(channel="ideal", packet_size=32))
    assert result["payload"] == payload
    assert semantic.decode(result["payload"])["text"] == text * 30
    assert result["metrics"]["raw_ber"] == 0


def test_packet_crc_and_bounds():
    packet = segment(b"abcdef", uuid4(), "semantic", "kn", 32)[0]
    raw = packet.serialize()
    assert Packet.parse(raw) == packet
    corrupt = bytearray(raw)
    corrupt[-5] ^= 1
    with pytest.raises(ApplicationError, match="CRC"):
        Packet.parse(bytes(corrupt))
    with pytest.raises(ApplicationError):
        Packet.parse(raw[:-1])
    with pytest.raises(ApplicationError):
        segment(b"", uuid4(), "semantic", "en", 32)
