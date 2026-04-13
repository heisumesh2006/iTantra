"""Explicit CPU evaluation of a pinned Kannada CTC checkpoint; no remote inference."""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.core.config import MODEL_CACHE
from app.services.metrics import text_scores
from huggingface_hub import snapshot_download
import soundfile as sf
import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

sys.stdout.reconfigure(encoding="utf-8")
MODEL_ID = "Harveenchadha/vakyansh-wav2vec2-kannada-knm-560"
REVISION = "0564782ee3f5a47f1db8af94bcdc942bb0d5bb29"
directory = MODEL_CACHE / "kannada-vakyansh"
print("Downloading pinned public Kannada checkpoint (~378 MB)", flush=True)
snapshot_download(
    MODEL_ID,
    revision=REVISION,
    local_dir=directory,
    allow_patterns=["*.json", "pytorch_model.bin"],
    max_workers=2,
)
torch.set_num_threads(2)
started = time.perf_counter()
processor = Wav2Vec2Processor.from_pretrained(directory, local_files_only=True)
model = Wav2Vec2ForCTC.from_pretrained(directory, local_files_only=True, weights_only=True).eval()
audio, rate = sf.read(ROOT / "research/results/smoke/kn-synthetic.wav", dtype="float32")
assert rate == 16000
inputs = processor(audio, sampling_rate=rate, return_tensors="pt")
with torch.inference_mode():
    logits = model(**inputs).logits
text = processor.batch_decode(torch.argmax(logits, dim=-1), skip_special_tokens=True)[0].strip()
reference = "ನಮಸ್ಕಾರ. ಇದು ನಮ್ಮ ಧ್ವನಿಯ ಪರೀಕ್ಷೆ."
report = {
    "model": MODEL_ID,
    "revision": REVISION,
    "provider": "Vakyansh Kannada wav2vec2 CTC",
    "source": "MMS-generated Kannada speech, not a human accuracy benchmark",
    "text": text,
    "reference": reference,
    "native_script_observed": any(0x0C80 <= ord(c) < 0x0D00 for c in text),
    "processing_ms_including_load": (time.perf_counter() - started) * 1000,
    "duration_seconds": len(audio) / rate,
    **text_scores(reference, text),
    "license_note": "Upstream Vakyansh model repository is MIT; HF conversion has no model card/license declaration. Do not redistribute weights without resolving terms.",
}
output = ROOT / "research/results/resume-2026-10-13"
output.mkdir(parents=True, exist_ok=True)
(output / "kannada-ctc-probe.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
if report["native_script_observed"] and text:
    model.save_pretrained(directory, safe_serialization=True)
    processor.save_pretrained(directory)
    print("Safe local checkpoint saved; provider selection has not changed.", flush=True)
