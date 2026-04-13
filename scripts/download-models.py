"""Explicit model download. No recordings are uploaded; runtime remains offline."""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.core.config import MODEL_CACHE, WHISPER_MODEL
from speech.registry import LANGUAGES
from huggingface_hub import snapshot_download

parser = argparse.ArgumentParser(description="Research-only MMS/EnCodec checkpoints use CC-BY-NC-4.0")
parser.add_argument(
    "--stt", action="store_true", help="Configured Whisper checkpoint; small ~500 MB, tiny ~75 MB"
)
parser.add_argument("--tts", nargs="*", choices=list(LANGUAGES), default=[], help="~145 MB per language")
parser.add_argument("--neural", action="store_true", help="EnCodec 24 kHz ~100 MB")
parser.add_argument("--kannada-asr", action="store_true", help="Pinned public Vakyansh Kannada CTC (~378 MB)")
args = parser.parse_args()
targets = []
if args.stt:
    targets.append(
        (
            f"Systran/faster-whisper-{WHISPER_MODEL}",
            f"whisper-{WHISPER_MODEL}",
            [
                "model.bin",
                "config.json",
                "tokenizer.json",
                "vocabulary.*",
                "preprocessor_config.json",
            ],
        )
    )
for language in args.tts:
    targets.append(
        (
            f"facebook/mms-tts-{LANGUAGES[language]['mms']}",
            f"tts-{language}",
            ["*.json", "*.safetensors", "*.txt"],
        )
    )
if args.neural:
    targets.append(("facebook/encodec_24khz", "encodec-24khz", ["*.json", "*.safetensors"]))
for repository, name, patterns in targets:
    print("Downloading", repository, "to", name, flush=True)
    snapshot_download(repository, local_dir=MODEL_CACHE / name, allow_patterns=patterns, max_workers=2)
if args.kannada_asr:
    subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "scripts/download-kannada-asr.py")], check=True)
print("Downloads complete. Run scripts/verify-models.py to record inference evidence.")
