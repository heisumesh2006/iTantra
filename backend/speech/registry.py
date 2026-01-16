from app.core.config import ROOT

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
