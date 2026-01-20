import time
from abc import ABC, abstractmethod
from functools import lru_cache
import numpy as np
from app.core.config import WHISPER_MODEL
from app.core.errors import ApplicationError
from app.services.audio import resample
from speech.registry import LANGUAGES, stt_path


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


class FasterWhisperProvider(SpeechRecognitionProvider):
    def transcribe(self, audio, sample_rate: int, language: str) -> dict:
        if language not in LANGUAGES:
            raise ApplicationError("Unsupported language")
        if np.sqrt(np.mean(audio**2)) < 0.001:
            raise ApplicationError("Recording is silent; record speech and retry", "silence")
        start = time.perf_counter()
        segments, info = whisper().transcribe(
            resample(audio, sample_rate, 16000),
            language=language,
            beam_size=3,
            vad_filter=False,
            condition_on_previous_text=False,
        )
        segments = list(segments)
        text = " ".join(s.text.strip() for s in segments).strip()
        if not text:
            raise ApplicationError("No speech recognized; try a clearer recording", "no_speech")
        return {
            "text": text,
            "language": info.language,
            "provider": "faster-whisper",
            "model": f"Systran/faster-whisper-{WHISPER_MODEL}",
            "processing_ms": (time.perf_counter() - start) * 1000,
            "confidence": None,
            "native_script_observed": any(
                {"hi": 0x0900, "kn": 0x0C80, "ta": 0x0B80, "te": 0x0C00, "ml": 0x0D00}.get(language, 0)
                <= ord(char)
                < {"hi": 0x0980, "kn": 0x0D00, "ta": 0x0C00, "te": 0x0C80, "ml": 0x0D80}.get(
                    language, 0x10000
                )
                for char in text
            ),
            "diagnostics": [
                {
                    "start": s.start,
                    "end": s.end,
                    "avg_logprob": s.avg_logprob,
                    "no_speech_probability": s.no_speech_prob,
                }
                for s in segments
            ],
        }
