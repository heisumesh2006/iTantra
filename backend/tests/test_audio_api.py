import io
import time
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


def test_upload_transmission_persistence_and_failure(client):
    raw, _ = wav()
    response = client.post("/api/v1/audio", files={"file": ("source.wav", raw, "audio/wav")})
    assert response.status_code == 201
    media = response.json()
    assert media["sample_rate"] == 16000
    assert client.get(media["url"]).status_code == 200
    for channel, expected in [
        ({"channel": "ideal"}, "recovered"),
        ({"channel": "ideal", "erasure_rate": 1}, "failed"),
    ]:
        response = client.post(
            "/api/v1/transmissions",
            json={"media_id": media["id"], "mode": "conventional", "channel_config": channel},
        )
        assert response.status_code == 202
        identifier = response.json()["id"]
        for _ in range(120):
            job = client.get("/api/v1/transmissions/" + identifier).json()
            if job["status"] not in ("queued", "running"):
                break
            time.sleep(0.05)
        assert job["status"] == "completed", job
        assert job["result"]["recovery_status"] == expected
        if expected == "failed":
            assert job["result"]["receiver"] is None
        assert client.get(f"/api/v1/exports/transmissions/{identifier}?format=csv").status_code == 200
        assert any(j["id"] == identifier for j in client.get("/api/v1/transmissions").json())


def test_missing_provider_and_silence(client, monkeypatch):
    from speech import providers

    monkeypatch.setattr(
        providers, "tts_path", lambda language: __import__("pathlib").Path("nonexistent-test-provider")
    )
    providers.mms.cache_clear()
    response = client.post("/api/v1/speech/synthesize", json={"text": "hello", "language": "ta"})
    assert response.status_code == 503 and response.json()["error"]["code"] == "model_unavailable"
    with pytest.raises(Exception, match="silent"):
        providers.STT.transcribe(np.zeros(16000), 16000, "en")
