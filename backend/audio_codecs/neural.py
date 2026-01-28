import json
import struct
from functools import lru_cache
import numpy as np
from app.core.errors import ApplicationError
from app.services.audio import resample
from speech.registry import neural_path, has_weights


@lru_cache(maxsize=1)
def model():
    if not has_weights(neural_path()):
        raise ApplicationError(
            "EnCodec weights missing. Run scripts/download-models.py --neural", "model_unavailable", 503
        )
    from transformers import EncodecModel

    return EncodecModel.from_pretrained(neural_path(), local_files_only=True).eval()


def encode(audio, rate: int, bandwidth: float) -> bytes:
    import torch

    if bandwidth not in (1.5, 3, 6, 12):
        raise ApplicationError("Unsupported EnCodec bandwidth")
    codec = model()
    waveform = resample(audio, rate, 24000)
    with torch.inference_mode():
        encoded = codec.encode(torch.from_numpy(waveform).reshape(1, 1, -1), bandwidth=bandwidth)
    codes = encoded.audio_codes.cpu().numpy()
    if any(scale is not None for scale in encoded.audio_scales):
        raise ApplicationError("This serializer requires the unnormalized mono 24 kHz model")
    values = codes.ravel().astype(np.uint16)
    bits = ((values[:, None] >> np.arange(9, -1, -1)) & 1).astype(np.uint8).ravel()
    metadata = json.dumps(
        {
            "model": "facebook/encodec_24khz",
            "shape": list(codes.shape),
            "samples": len(waveform),
            "rate": 24000,
            "bandwidth": bandwidth,
            "token_bits": 10,
        },
        separators=(",", ":"),
    ).encode()
    return b"EC10" + struct.pack(">I", len(metadata)) + metadata + np.packbits(bits).tobytes()
