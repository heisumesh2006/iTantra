# Transmission Pipelines

A: normalized source → FFmpeg Opus 12 kbps target, 20 ms frames → Ogg bytes → packets → DSP → exact Ogg bytes → Opus decode.

B: resample 24 kHz → EnCodec encode → packed 10-bit codebook indices plus bounded JSON metadata → packets/DSP → strict envelope recovery → EnCodec decode → trim model padding.

C: resample 16 kHz → Whisper transcript (or configured Kannada Vakyansh CTC transcript) (or explicitly selected manual text) → NFC UTF-8 JSON, shorter-of-zlib/raw envelope → packets/DSP → recovered text → local language-specific MMS VITS.

D: explainable rule recommendation based on objective, model availability, budget and latency tolerance, with channel warnings; then execute the selected actual pipeline. Budget and latency targets are evaluated afterward, not guaranteed.
