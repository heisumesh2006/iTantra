# Demo Script

1. Start both servers. Show the simulation label and connected backend.
2. Upload research/results/smoke/en-synthetic.wav, explicitly identifying it as synthetic. Select Conventional and Ideal; transmit and play reconstructed audio.
3. Repeat Neural at 3 kbps; compare serialized payload and wire cost.
4. Repeat Semantic, inspect sender and receiver text, play reconstructed speech. Speaker identity is not preserved.
5. Upload research/results/smoke/kn-synthetic.wav, choose Kannada and Semantic with Ideal channel. The configured Vakyansh provider recognizes native Kannada, packets recover it, and MMS generates receiver speech. Show both transcripts and the measured punctuation/character errors. Repeat Hindi to expose its real recognition errors. Label all supplied smoke audio synthetic.
6. Set AWGN Es/N0 to 4 dB or 100% erasure to demonstrate failed CRC/missing payload and absent receiver audio.
7. In Channel Lab run a seeded sweep and compare empirical versus analytical BER.
8. Run a same-source batch in Analytics and export results. Open History to show persisted metadata.
Evaluator Q&A: Is it radio hardware? No, software DSP with specified assumptions. Are models trained here? Speech/codec models are pretrained; the separate small feature-channel network has its own measured training run. Does CRC fix bits? No. Is semantic bitrate a guaranteed gain? It is a measured message-size comparison with recognition and identity tradeoffs, not a universal quality claim.
