import json
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


def verified():
    if not VERIFICATION.exists():
        return {}
    return json.loads(VERIFICATION.read_text(encoding="utf-8"))


def languages():
    evidence = verified()
    entries = []
    for code, info in LANGUAGES.items():
        descriptor = selected_stt(code)
        tts_installed = find_spec("transformers") is not None and has_weights(tts_path(code))
        if code == "kn" and KANNADA_STT == "vakyansh":
            check = evidence.get("providers", {}).get("kn", {})
            stt_checked = check.get("cache_key") == descriptor["cache_key"] and check.get(
                "native_script_verified", False
            )
            roundtrip_checked = stt_checked and check.get("roundtrip_verified", False)
        else:
            stt_checked = (
                code in evidence.get("semantic_verified", []) and evidence.get("stt_model") == stt_path().name
            )
            roundtrip_checked = stt_checked
        ready = bool(descriptor["installed"] and tts_installed and roundtrip_checked)
        status = (
            "Round trip tested (synthetic)"
            if ready
            else "Experimental"
            if descriptor["installed"] and tts_installed
            else "STT installed; TTS not installed"
            if descriptor["installed"]
            else "Not installed"
        )
        entries.append(
            {
                "code": code,
                **info,
                "stt_installed": descriptor["installed"],
                "tts_installed": tts_installed,
                "stt_verified": bool(descriptor["installed"] and stt_checked),
                "tts_verified": tts_installed and code in evidence.get("tts", []),
                "roundtrip_verified": ready,
                "status": status,
                "tts_model": f"facebook/mms-tts-{info['mms']}",
                "stt_model": descriptor["model"],
                "stt_provider": descriptor["provider"],
                "stt_revision": descriptor["revision"],
                "quality_validation": "No human-speech benchmark; smoke verification uses synthetic speech",
            }
        )
    return entries


def capabilities():
    return {
        "simulation_mode": True,
        "hardware": "No RF hardware attached",
        "device": "CPU",
        "conventional": {"installed": True, "provider": "FFmpeg libopus", "target_kbps": 12},
        "neural": {
            "installed": find_spec("transformers") is not None and has_weights(neural_path()),
            "verified": bool(verified().get("neural")),
            "model": "facebook/encodec_24khz",
            "bandwidths": [1.5, 3, 6, 12],
            "license": "CC-BY-NC-4.0",
        },
        "languages": languages(),
        "stt": {
            "provider": "Local per-language router",
            "model": WHISPER_MODEL,
            "kannada_provider": KANNADA_STT,
            "compute_type": "int8",
            "confidence": "Not available; segment log probability is diagnostic only",
        },
        "tts": {"provider": "Meta MMS VITS", "license": "CC-BY-NC-4.0; research/noncommercial use"},
        "privacy": "Offline local inference; no audio sent to external services. Models download only via script.",
        "verification": verified(),
    }
