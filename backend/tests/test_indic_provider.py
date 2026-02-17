import numpy as np
import pytest
from app.core.errors import ApplicationError
from speech.indic_ctc import VakyanshKannadaProvider


def test_language_boundary_and_silence():
    provider = VakyanshKannadaProvider()
    with pytest.raises(ApplicationError, match="Kannada only"):
        provider.transcribe(np.ones(16000), 16000, "en")
    with pytest.raises(ApplicationError, match="silent"):
        provider.transcribe(np.zeros(16000), 16000, "kn")
