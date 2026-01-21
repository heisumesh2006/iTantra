"""Pinned local Kannada CTC provider. No transliteration, cloud calls or runtime downloads."""

import time
from functools import lru_cache
import numpy as np
from app.core.errors import ApplicationError
from app.services.audio import resample
from speech.providers import SpeechRecognitionProvider
from speech.registry import KANNADA_MODEL, KANNADA_REVISION, kannada_path, has_weights


@lru_cache(maxsize=1)
def kannada_model():
    if not has_weights(kannada_path()):
        raise ApplicationError(
            "Kannada CTC safetensors missing. Run scripts/download-kannada-asr.py explicitly.",
            "model_unavailable",
            503,
        )
    import torch
    from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

    torch.set_num_threads(2)
    processor = Wav2Vec2Processor.from_pretrained(kannada_path(), local_files_only=True)
    model = Wav2Vec2ForCTC.from_pretrained(
        kannada_path(), local_files_only=True, use_safetensors=True, trust_remote_code=False
    ).eval()
    return processor, model


class VakyanshKannadaProvider(SpeechRecognitionProvider):
    def transcribe(self, audio, sample_rate: int, language: str) -> dict:
        if language != "kn":
            raise ApplicationError("This CTC checkpoint supports Kannada only", "unsupported_language")
        if len(audio) == 0 or not np.isfinite(audio).all() or np.sqrt(np.mean(audio**2)) < 0.001:
            raise ApplicationError("Recording is silent or invalid; record speech and retry", "silence")
        started = time.perf_counter()
        processor, model = kannada_model()
        import torch

        waveform = resample(audio, sample_rate, 16000)
        inputs = processor(waveform, sampling_rate=16000, return_tensors="pt")
        with torch.inference_mode():
            predicted = model(**inputs).logits.argmax(dim=-1)
        # Match standard Transformers ASR decoding; reserved BOS/EOS markers are not speech.
        text = processor.batch_decode(predicted, skip_special_tokens=True)[0].strip()
        native = any(0x0C80 <= ord(char) < 0x0D00 for char in text)
        if not text or not native:
            raise ApplicationError("Kannada recognizer returned no native-script speech", "no_speech")
        return {
            "text": text,
            "language": "kn",
            "provider": "Vakyansh Kannada wav2vec2 CTC",
            "model": KANNADA_MODEL,
            "revision": KANNADA_REVISION,
            "processing_ms": (time.perf_counter() - started) * 1000,
            "confidence": None,
            "native_script_observed": native,
            "diagnostics": {
                "decoding": "greedy CTC; standard special-token removal",
                "input_samples": len(waveform),
                "sample_rate": 16000,
            },
        }
