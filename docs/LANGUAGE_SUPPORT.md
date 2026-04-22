# Verified language coverage

As of 13 October 2026. `GET /api/v1/languages` reports selected provider, checkpoint installation, provider-specific executed evidence and synthetic round-trip status separately.

| Language | Recognition | Synthesis | Actual full-path evidence |
|---|---|---|---|
| English | Whisper small CPU int8, tested | MMS eng, tested | Synthetic utterance: A/B/C and browser playback passed |
| Hindi | Whisper small CPU int8, tested with errors | MMS hin, tested | Synthetic speech semantic path passed |
| Kannada | Pinned Vakyansh wav2vec2 CTC, native script tested | MMS kan, tested | Three synthetic utterances plus browser semantic path passed |
| Tamil | Shared Whisper checkpoint present; language unverified | MMS tam not installed | No complete speech round trip |
| Telugu | Shared Whisper checkpoint present; language unverified | MMS tel not installed | No complete speech round trip |
| Malayalam | Shared Whisper checkpoint present; language unverified | MMS mal not installed | No complete speech round trip |

All six scripts pass byte/Unicode transport tests. That does not establish speech accuracy or TTS availability. UI status “Round trip tested (synthetic)” replaces the broader “Fully supported” wording. Native script and successful payload recovery do not guarantee correct recognition, intelligibility or identity preservation. Human-speech benchmarks remain pending.

Optional synthesis downloads: `.venv/Scripts/python.exe -X utf8 scripts/download-models.py --tts ta te ml`. Install and execute actual language tests before changing their verified status.
