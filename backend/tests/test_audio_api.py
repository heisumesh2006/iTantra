import io
import numpy as np
import pytest
import soundfile as sf
from fastapi.testclient import TestClient
from app.main import app
from app.services.audio import resample
from audio_codecs import conventional


@pytest.fixture
def client(tmp_path, monkeypatch):
    from app.db import store

    monkeypatch.setattr(store, "DB", tmp_path / "test.sqlite3")
    from app.services import audio

    monkeypatch.setattr(audio, "MEDIA", tmp_path)
    with TestClient(app) as c:
        yield c


def wav():
    rate = 16000
    x = (0.2 * np.sin(2 * np.pi * 440 * np.arange(rate) / rate)).astype(np.float32)
    buf = io.BytesIO()
    sf.write(buf, x, rate, format="WAV", subtype="PCM_16")
    return buf.getvalue(), x


def test_resample_frequency_and_length():
    _, x = wav()
    y = resample(x, 16000, 24000)
    assert len(y) == 24000
    assert np.argmax(abs(np.fft.rfft(y))) == 440


def test_real_opus_roundtrip():
    _, x = wav()
    payload = conventional.encode(x, 16000)
    output, rate = conventional.decode(payload)
    assert payload[:4] == b"OggS" and len(payload) < len(x) * 2
    assert rate == 16000 and abs(len(output) - len(x)) < 320
    assert np.isfinite(output).all() and np.std(output) > 0.01


def test_health_validation_and_safe_media_ids(client):
    assert client.get("/api/v1/health").json()["simulation_mode"] is True
    assert client.get("/api/v1/media/not-a-uuid").status_code == 422
    assert client.post("/api/v1/transmissions", json={}).status_code == 400
    assert client.post("/api/v1/channels/simulate", json={"config": {"packet_size": 1}}).status_code == 422
    assert client.post("/api/v1/audio", files={"file": ("danger.exe", b"bad")}).status_code == 400
    assert client.post("/api/v1/audio", files={"file": ("bad.wav", b"not audio")}).status_code == 400
