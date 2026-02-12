from uuid import UUID, uuid4
import numpy as np
import pytest
from scipy.special import erfc
from app.core.errors import ApplicationError
from app.schemas.requests import ChannelConfig
from radio.packets import Packet, segment, reassemble, HEADER
from radio.modulation import modulate, demodulate
from radio.channel import transport, apply_channel
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


def test_missing_duplicate_and_foreign_sessions():
    packets = segment(b"a" * 100, uuid4(), "semantic", "en", 32)
    assert reassemble(packets[::-1]) == b"a" * 100
    for invalid in (
        packets[:-1],
        packets[:-1] + [packets[0]],
        packets[:-1] + segment(b"x" * 100, uuid4(), "semantic", "en", 32)[-1:],
    ):
        with pytest.raises(ApplicationError):
            reassemble(invalid)


@pytest.mark.parametrize("modulation", ["BPSK", "QPSK"])
@pytest.mark.parametrize("repetition", [1, 3])
def test_exact_bit_accounting(modulation, repetition):
    payload = b"x" * 70
    result = transport(
        payload,
        uuid4(),
        "conventional",
        "en",
        ChannelConfig(channel="ideal", packet_size=32, modulation=modulation, repetition=repetition),
    )
    m = result["metrics"]
    assert m["payload_bits"] == 560
    assert m["framing_overhead_bits"] == 3 * (HEADER.size + 4) * 8
    assert m["total_transmitted_bits"] == m["framed_bits"] * repetition
    assert m["recovered_bits"] == 560
    assert m["packet_delivery_rate"] == 1


@pytest.mark.parametrize("modulation", ["BPSK", "QPSK"])
def test_awgn_agrees_with_theory(modulation):
    rng = np.random.default_rng(99)
    bits = rng.integers(0, 2, 400000, dtype=np.uint8)
    symbols, padding = modulate(bits, modulation)
    snr = 3
    _, equalized = apply_channel(symbols, "awgn", snr, rng)
    empirical = np.mean(bits != demodulate(equalized, modulation, padding))
    bps = 1 if modulation == "BPSK" else 2
    p = float(0.5 * erfc(np.sqrt(10 ** (snr / 10) / bps)))
    tolerance = 6 * np.sqrt(p * (1 - p) / len(bits))
    assert abs(empirical - p) < tolerance


def test_awgn_noise_energy_and_rayleigh_reference():
    rng = np.random.default_rng(11)
    symbols = np.ones(400000, dtype=np.complex128)
    received, _ = apply_channel(symbols, "awgn", 5, rng)
    assert np.mean(np.abs(received - symbols) ** 2) == pytest.approx(10 ** (-0.5), rel=0.012)
    _, equalized = apply_channel(symbols, "rayleigh", 5, rng)
    p = 0.5 * (1 - np.sqrt(10**0.5 / (1 + 10**0.5)))
    assert np.mean(equalized.real < 0) == pytest.approx(p, abs=0.002)


def test_seed_reproducibility_and_erasure():
    session = UUID(int=42)
    config = ChannelConfig(snr_db=2)
    a = transport(b"x" * 300, session, "semantic", "en", config)
    b = transport(b"x" * 300, session, "semantic", "en", config)
    assert a["packets"] == b["packets"] and a["constellation"] == b["constellation"]
    assert a["metrics"]["raw_ber"] == b["metrics"]["raw_ber"]
    lost = transport(b"x" * 300, session, "semantic", "en", ChannelConfig(erasure_rate=1))
    assert lost["payload"] is None and lost["metrics"]["raw_ber"] is None
    assert lost["metrics"]["packet_delivery_rate"] == 0


def test_controlled_corruption_is_not_recovered():
    result = transport(
        b"Unicode valid source", uuid4(), "semantic", "en", ChannelConfig(channel="ideal", bit_flip_rate=0.5)
    )
    assert result["payload"] is None
    assert result["metrics"]["raw_ber"] > 0.35
