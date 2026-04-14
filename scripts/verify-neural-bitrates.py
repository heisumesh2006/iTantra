import json
import sys
import time
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from audio_codecs import neural

audio, rate = sf.read(ROOT / "research/results/smoke/en-synthetic.wav", dtype="float32")
results = []
for bandwidth in [1.5, 3, 6, 12]:
    started = time.perf_counter()
    payload = neural.encode(audio, rate, bandwidth)
    recovered, decoded_rate = neural.decode(payload)
    assert decoded_rate == 24000 and len(recovered) > 0 and np.isfinite(recovered).all()
    results.append(
        {
            "target_kbps": bandwidth,
            "serialized_bytes": len(payload),
            "payload_bps": len(payload) * 8 / (len(audio) / rate),
            "duration_ms": (time.perf_counter() - started) * 1000,
            "decode_finite": True,
        }
    )
destination = ROOT / "research/results/smoke/neural-bitrates.json"
destination.write_text(json.dumps(results, indent=2), encoding="utf-8")
print(json.dumps(results, indent=2))
