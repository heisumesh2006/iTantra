from functools import lru_cache
from app.core.errors import ApplicationError
from speech.registry import neural_path, has_weights


@lru_cache(maxsize=1)
def model():
    if not has_weights(neural_path()):
        raise ApplicationError(
            "EnCodec weights missing. Run scripts/download-models.py --neural", "model_unavailable", 503
        )
    from transformers import EncodecModel

    return EncodecModel.from_pretrained(neural_path(), local_files_only=True).eval()
