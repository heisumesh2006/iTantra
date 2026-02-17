import numpy as np
import pytest
from app.core.errors import ApplicationError
from speech import providers
from speech.indic_ctc import VakyanshKannadaProvider, kannada_model


def test_language_boundary_and_silence():
    provider = VakyanshKannadaProvider()
    with pytest.raises(ApplicationError, match="Kannada only"):
        provider.transcribe(np.ones(16000), 16000, "en")
    with pytest.raises(ApplicationError, match="silent"):
        provider.transcribe(np.zeros(16000), 16000, "kn")


def test_missing_ctc_weights_are_explicit(monkeypatch, tmp_path):
    from speech import indic_ctc

    monkeypatch.setattr(indic_ctc, "kannada_path", lambda: tmp_path)
    kannada_model.cache_clear()
    with pytest.raises(ApplicationError, match="safetensors missing"):
        kannada_model()
    with pytest.raises(ApplicationError, match="safetensors missing"):
        VakyanshKannadaProvider().transcribe(np.ones(16000), 16000, "kn")


def test_router_keeps_non_kannada_whisper(monkeypatch):
    from app.core import config

    monkeypatch.setattr(config, "KANNADA_STT", "vakyansh")
    router = providers.LocalRecognitionRouter()

    def observed(audio, rate, language):
        raise ApplicationError("Whisper route reached: " + language)

    monkeypatch.setattr(router.whisper_provider, "transcribe", observed)
    with pytest.raises(ApplicationError, match="Whisper route reached: hi"):
        router.transcribe(np.ones(16000), 16000, "hi")
