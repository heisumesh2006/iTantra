# Stt Tts Integration

SpeechRecognitionProvider and SpeechSynthesisProvider abstractions live in backend/speech/providers.py. Faster Whisper uses CPU int8 Whisper small, beam 3, fixed input language and local-only weights. Segment log probabilities are diagnostics, not confidence. MMS VITS uses language-specific checkpoints, deterministic random seed 42 and native tokenizer romanization where configured. Models load lazily. English/Hindi/Kannada checkpoints are installed; use verified.json and VERIFICATION_REPORT for actual executed-language evidence. Tiny Whisper has limited Indic recognition quality. AI4Bharat IndicConformer was considered but is not installed due its larger resource footprint and integration requirements; it is a future provider, not a hidden fallback.


Verified on 13 October 2026: English and Hindi semantic speech round trips use local Whisper small; Kannada now uses a pinned public Vakyansh wav2vec2 CTC checkpoint and completed three synthetic speech round trips with native-script text. The old Whisper Kannada wrong-script failure remains in historical evidence. Tamil/Telugu/Malayalam TTS checkpoints are not installed; their shared Whisper checkpoint is present but language-specific recognition quality is not verified. No human-speech accuracy benchmark exists.


LocalRecognitionRouter selects Kannada Vakyansh CTC only when configured, with lazy local safetensors loading. Capability evidence is tied to the selected per-language model/revision; stale Whisper evidence cannot certify a different Kannada provider. See KANNADA_ASR.md and LANGUAGE_SUPPORT.md.
