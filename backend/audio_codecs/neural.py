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


def decode(payload: bytes):
    import torch

    if payload[:4] != b"EC10" or len(payload) < 8:
        raise ApplicationError("Invalid neural codec envelope")
    header_size = struct.unpack(">I", payload[4:8])[0]
    if not 0 < header_size <= 1024 or len(payload) < 8 + header_size:
        raise ApplicationError("Invalid neural metadata length")
    metadata = json.loads(payload[8 : 8 + header_size])
    shape = metadata["shape"]
    if metadata["model"] != "facebook/encodec_24khz" or len(shape) != 4 or shape[:2] != [1, 1]:
        raise ApplicationError("Unsupported neural model or tensor shape")
    if shape[2] not in (2, 4, 8, 16) or not 1 <= shape[3] <= 5000 or not 1 <= metadata["samples"] <= 1440000:
        raise ApplicationError("Neural token bounds invalid")
    count = int(np.prod(shape))
    packed = payload[8 + header_size :]
    if len(packed) != (count * 10 + 7) // 8:
        raise ApplicationError("Neural token stream length mismatch")
    bits = np.unpackbits(np.frombuffer(packed, dtype=np.uint8))[: count * 10].reshape(count, 10)
    codes = (bits.astype(np.int64) @ (1 << np.arange(9, -1, -1))).reshape(shape)
    with torch.inference_mode():
        waveform = model().decode(torch.from_numpy(codes), [None]).audio_values[0, 0].cpu().numpy()
    return waveform[: metadata["samples"]], 24000
