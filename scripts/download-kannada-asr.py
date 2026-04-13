"""Explicit public checkpoint download and restricted tensor-to-safetensors conversion."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from speech.registry import KANNADA_MODEL, KANNADA_REVISION, kannada_path
from huggingface_hub import snapshot_download

print("Downloading ~378 MB Kannada CTC checkpoint. Inference stays local.", flush=True)
print(
    "Upstream Vakyansh repository: MIT. HF conversion has no model-card license; resolve redistribution terms separately.",
    flush=True,
)
snapshot_download(
    KANNADA_MODEL,
    revision=KANNADA_REVISION,
    local_dir=kannada_path(),
    allow_patterns=["*.json", "pytorch_model.bin"],
    max_workers=2,
)
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

model = Wav2Vec2ForCTC.from_pretrained(kannada_path(), local_files_only=True, weights_only=True).eval()
processor = Wav2Vec2Processor.from_pretrained(kannada_path(), local_files_only=True)
model.save_pretrained(kannada_path(), safe_serialization=True)
processor.save_pretrained(kannada_path())
print("Local safetensors ready. Select ITANTRA_KANNADA_STT=vakyansh and restart the backend.", flush=True)
