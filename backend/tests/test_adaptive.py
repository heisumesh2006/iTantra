from app.schemas.requests import TransmissionRequest
from transceiver import adaptive


def cap(speech=True, neural=True):
    return {
        "languages": [
            {
                "code": "en",
                "stt_installed": speech,
                "tts_installed": speech,
                "status": "Fully supported (smoke tested)" if speech else "Not installed",
            }
        ],
        "neural": {"installed": neural},
    }


def test_low_budget_meaning_prefers_verified_semantics(monkeypatch):
    monkeypatch.setattr(adaptive, "capabilities", lambda: cap())
    assert adaptive.recommend(TransmissionRequest(mode="adaptive", budget_kbps=2))["mode"] == "semantic"


def test_missing_speech_prefers_installed_neural(monkeypatch):
    monkeypatch.setattr(adaptive, "capabilities", lambda: cap(False, True))
    assert adaptive.recommend(TransmissionRequest(mode="adaptive", budget_kbps=3))["mode"] == "neural"
