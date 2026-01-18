from importlib.util import find_spec
from app.core.config import MODEL_CACHE, ROOT, WHISPER_MODEL, KANNADA_STT

KANNADA_MODEL = "Harveenchadha/vakyansh-wav2vec2-kannada-knm-560"
KANNADA_REVISION = "0564782ee3f5a47f1db8af94bcdc942bb0d5bb29"

LANGUAGES = {
    "en": {"name": "English", "native": "English", "mms": "eng"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "mms": "hin"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "mms": "kan"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "mms": "tam"},
    "te": {"name": "Telugu", "native": "తెలుగు", "mms": "tel"},
    "ml": {"name": "Malayalam", "native": "മലയാളം", "mms": "mal"},
}
VERIFICATION = ROOT / "models" / "verified.json"


def stt_path():
    return MODEL_CACHE / f"whisper-{WHISPER_MODEL}"


def kannada_path():
    return MODEL_CACHE / "kannada-vakyansh"


def selected_stt(language: str) -> dict:
    if language == "kn" and KANNADA_STT == "vakyansh":
        return {
            "provider": "Vakyansh Kannada wav2vec2 CTC",
            "model": KANNADA_MODEL,
            "revision": KANNADA_REVISION,
            "cache_key": "vakyansh-kannada@" + KANNADA_REVISION,
            "installed": find_spec("transformers") is not None and has_weights(kannada_path()),
        }
    return {
        "provider": "faster-whisper",
        "model": f"Systran/faster-whisper-{WHISPER_MODEL}",
        "cache_key": stt_path().name,
        "revision": None,
        "installed": find_spec("faster_whisper") is not None and (stt_path() / "model.bin").is_file(),
    }


def tts_path(language: str):
    return MODEL_CACHE / f"tts-{language}"


def neural_path():
    return MODEL_CACHE / "encodec-24khz"


def has_weights(path):
    return path.is_dir() and any(path.glob("*.safetensors")) and (path / "config.json").is_file()
