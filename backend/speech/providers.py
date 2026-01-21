import time
from abc import ABC, abstractmethod
from functools import lru_cache
import numpy as np
from app.core.config import WHISPER_MODEL
from app.core.errors import ApplicationError
from app.services.audio import resample
from speech.registry import LANGUAGES, stt_path, tts_path, has_weights


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


@lru_cache(maxsize=2)
def mms(language: str):
    path = tts_path(language)
    if not has_weights(path):
        raise ApplicationError(
            f"TTS weights missing for {language}. Run scripts/download-models.py --tts {language}",
            "model_unavailable",
            503,
        )
    from transformers import AutoTokenizer, VitsModel
    import torch

    torch.set_num_threads(2)
    tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True, trust_remote_code=False)
    model = VitsModel.from_pretrained(path, local_files_only=True).eval()
    return tokenizer, model


class MMSProvider(SpeechSynthesisProvider):
    def synthesize(self, text: str, language: str):
        if language not in LANGUAGES or not text.strip() or len(text) > 1000:
            raise ApplicationError("TTS requires a supported language and 1–1000 characters")
        start = time.perf_counter()
        tokenizer, model = mms(language)
        import torch

        inputs = tokenizer(text, return_tensors="pt")
        if inputs["input_ids"].numel() == 0:
            raise ApplicationError("Text has no tokens supported by this TTS model")
        # fork_rng confines deterministic synthesis to this call.
        with torch.random.fork_rng(), torch.inference_mode():
            torch.manual_seed(42)
            waveform = model(**inputs).waveform[0].cpu().numpy()
        return (
            waveform,
            model.config.sampling_rate,
            {
                "provider": "Meta MMS VITS",
                "model": f"facebook/mms-tts-{LANGUAGES[language]['mms']}",
                "processing_ms": (time.perf_counter() - start) * 1000,
                "license": "CC-BY-NC-4.0",
            },
        )


class LocalRecognitionRouter(SpeechRecognitionProvider):
    def __init__(self):
        self.whisper_provider = FasterWhisperProvider()

    def transcribe(self, audio, sample_rate: int, language: str) -> dict:
        from app.core.config import KANNADA_STT

        if language == "kn" and KANNADA_STT == "vakyansh":
            from speech.indic_ctc import VakyanshKannadaProvider

            return VakyanshKannadaProvider().transcribe(audio, sample_rate, language)
        if language == "kn" and KANNADA_STT not in ("whisper", "vakyansh"):
            raise ApplicationError(
                "ITANTRA_KANNADA_STT must be whisper or vakyansh", "invalid_configuration", 503
            )
        return self.whisper_provider.transcribe(audio, sample_rate, language)


STT = LocalRecognitionRouter()
TTS = MMSProvider()
