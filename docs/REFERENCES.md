# References

Primary implementation and model references:
- Faster Whisper: https://github.com/SYSTRAN/faster-whisper (CPU int8, multilingual recognition).
- MMS Kannada model card: https://huggingface.co/facebook/mms-tts-kan (CC-BY-NC-4.0).
- MMS paper: https://arxiv.org/abs/2305.13516 .
- EnCodec implementation: https://github.com/facebookresearch/encodec .
- EnCodec paper: https://arxiv.org/abs/2210.13438 .
- Transformers EnCodec: https://huggingface.co/docs/transformers/model_doc/encodec .
- AI4Bharat IndicConformer: https://huggingface.co/ai4bharat/indicconformer-600m-multilingual (considered, not installed).
- FLEURS: https://huggingface.co/datasets/google/fleurs (future evaluation; verify split/license terms).
- OpenSLR: https://www.openslr.org/ (dataset-specific licenses).
No external human dataset was downloaded for this build.

- Integrated Kannada CTC checkpoint: https://huggingface.co/Harveenchadha/vakyansh-wav2vec2-kannada-knm-560 (pinned revision in KANNADA_ASR.md).
- Vakyansh upstream model list: https://github.com/Open-Speech-EkStep/vakyansh-models .
