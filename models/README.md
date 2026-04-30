# Local model cache
Run `.venv/Scripts/python.exe -X utf8 scripts/download-models.py --stt --tts en hi kn --neural` explicitly. Runtime inference uses local-only checkpoints. No model downloads occur at startup. Whisper small is ~500 MB (tiny is ~75 MB); each MMS TTS is ~145 MB; EnCodec is ~100 MB. MMS and EnCodec weights are CC-BY-NC-4.0. Whisper is MIT. Weights and inference evidence are ignored by Git.

`scripts/verify-models.py` records executed inference in `verified.json`. A language labeled smoke tested was exercised on synthetic speech; that label does not establish quality on human speech. Additional TTS models can be installed with `--tts ta te ml`. Configure `ITANTRA_WHISPER_MODEL=small` and download `--stt` for a larger CPU recognizer; this increases disk and inference cost.


Verified on 13 October 2026: English and Hindi semantic speech round trips use local Whisper small; Kannada now uses a pinned public Vakyansh wav2vec2 CTC checkpoint and completed three synthetic speech round trips with native-script text. The old Whisper Kannada wrong-script failure remains in historical evidence. Tamil/Telugu/Malayalam TTS checkpoints are not installed; their shared Whisper checkpoint is present but language-specific recognition quality is not verified. No human-speech accuracy benchmark exists.


Kannada: use `--kannada-asr` to explicitly download/convert the pinned public CTC checkpoint, then select `ITANTRA_KANNADA_STT=vakyansh` in `.env`. Runtime only loads local safetensors. Source plus converted weights use about 756 MB. Conversion publisher has no explicit model-card license; weights are not redistributed.
