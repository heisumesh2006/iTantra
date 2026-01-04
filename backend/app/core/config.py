import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")
STORAGE = ROOT / "storage"
MEDIA = STORAGE / "media"
MODEL_CACHE = ROOT / "models" / "cache"
for directory in (MEDIA, MODEL_CACHE):
    directory.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("HF_HOME", str(MODEL_CACHE))
os.environ.setdefault("TORCH_HOME", str(MODEL_CACHE / "torch"))
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("OMP_NUM_THREADS", os.getenv("ITANTRA_CPU_THREADS", "2"))
MAX_BYTES = int(os.getenv("ITANTRA_MAX_UPLOAD_MB", "15")) * 1024 * 1024
MAX_SECONDS = int(os.getenv("ITANTRA_MAX_AUDIO_SECONDS", "60"))
RETENTION_HOURS = int(os.getenv("ITANTRA_RETENTION_HOURS", "24"))
WHISPER_MODEL = os.getenv("ITANTRA_WHISPER_MODEL", "small")
KANNADA_STT = os.getenv("ITANTRA_KANNADA_STT", "whisper")
