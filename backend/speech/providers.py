from abc import ABC, abstractmethod
from functools import lru_cache
from app.core.errors import ApplicationError
from speech.registry import stt_path


class SpeechRecognitionProvider(ABC):
    @abstractmethod
    def transcribe(self, audio, sample_rate: int, language: str) -> dict: ...


class SpeechSynthesisProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, language: str): ...


@lru_cache(maxsize=1)
def whisper():
    if not (stt_path() / "model.bin").is_file():
        raise ApplicationError(
            "Whisper weights missing. Run scripts/download-models.py --stt", "model_unavailable", 503
        )
    from faster_whisper import WhisperModel

    return WhisperModel(
        str(stt_path()),
        device="cpu",
        compute_type="int8",
        cpu_threads=2,
        num_workers=1,
        local_files_only=True,
    )
