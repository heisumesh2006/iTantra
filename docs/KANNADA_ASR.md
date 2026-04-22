# Kannada ASR integration and evidence

The original Whisper small Kannada smoke sample produced Devanagari, preventing Kannada MMS synthesis. This failure remains in `research/results/smoke/verification.json`. On 13 October 2026, a public Kannada-specific CTC checkpoint was evaluated and integrated only for Kannada. English/Hindi and the other baseline language routes retain Whisper.

Provider: `Harveenchadha/vakyansh-wav2vec2-kannada-knm-560`, pinned revision `0564782ee3f5a47f1db8af94bcdc942bb0d5bb29`. The checkpoint is approximately 378 MB and runs on the existing CPU PyTorch/Transformers installation. `backend/speech/indic_ctc.py` enforces Kannada, resamples to 16 kHz, uses greedy CTC argmax and omits reserved special tokens. No transliteration, spelling correction, reference-text substitution, cloud recognition or confidence score is introduced.

The initial raw decoding contained `<s>` control tokens. `skip_special_tokens=True` removes model control markers, not recognized words. The initial result is retained in `kannada-ctc-probe-initial.json`, and corrected decoding in `kannada-ctc-probe.json`. Runtime accepts only local safetensors and does not fetch or execute remote code. The download script loads the public source state dictionary using PyTorch's restricted `weights_only=True`, then saves safetensors.

Selection: `ITANTRA_KANNADA_STT=vakyansh` in `.env`, followed by backend restart. Set it to `whisper` to retain the previous baseline. Explicitly selecting missing CTC weights gives an actionable error, without silent provider replacement.

Three MMS-generated Kannada utterances completed the actual HTTP transmission path and receiver synthesis. The first source “ನಮಸ್ಕಾರ. ಇದು ನಮ್ಮ ಧ್ವನಿಯ ಪರೀಕ್ಷೆ.” produced “ನಮಸ್ಕಾರ ಇದು ನಮ್ಮ ಧ್ವನಿಯ ಪರೀಕ್ಷೆ”: CER 0.060606, WER 0.4 under existing punctuation-sensitive NFC/whitespace scoring. The second removed punctuation; the third added a final character. All errors are preserved in `research/results/resume-2026-10-13/api-verification.json`; this is not a human-speech benchmark. Provider-specific evidence is merged into `models/verified.json`, while historical Whisper evidence remains unchanged.

The official IndicConformer checkpoint was investigated but requires access approval/contact-information sharing and custom-code integration. It was not installed, no gate was bypassed, and it is not the active provider.

Primary sources:
- Converted CTC checkpoint: https://huggingface.co/Harveenchadha/vakyansh-wav2vec2-kannada-knm-560
- Vakyansh upstream models, Kannada knm_560 and MIT repository: https://github.com/Open-Speech-EkStep/vakyansh-models
- Official gated IndicConformer: https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual

The converted Hugging Face checkpoint has no explicit model-card license. Upstream's repository license must not be treated as an invented license declaration for a separate conversion. Weights remain local and ignored; resolve redistribution terms separately.
