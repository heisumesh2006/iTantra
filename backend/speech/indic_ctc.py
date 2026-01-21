"""Pinned local Kannada CTC provider. No transliteration, cloud calls or runtime downloads."""

from functools import lru_cache
from app.core.errors import ApplicationError
from speech.registry import kannada_path, has_weights


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
