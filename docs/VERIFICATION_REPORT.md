# iTantra completion and verification report

Verified 13 October 2026, Asia/Kolkata. Existing project: `C:\Users\umesh\Desktop\projects\iTantra`. The project was continued in place; source, prior results and Git repository were preserved.

## 1. Completion status

The local research prototype's demonstrated workflows are implemented and verified. The complete commercial/all-language vision remains incomplete. Real Opus, neural codec and semantic pipelines work. English, Hindi and Kannada complete synthetic speech round trips. Tamil, Telugu and Malayalam full speech paths remain unavailable because TTS weights are absent and language-specific ASR has not been validated. No claim of human-speech quality, physical radio deployment or continuous full-duplex operation is made.

## 2. Changes made during continuation

- Added a Kannada-only CPU Vakyansh wav2vec2 CTC provider, pinned at revision `0564782ee3f5a47f1db8af94bcdc942bb0d5bb29`. Whisper remains the provider for other languages.
- Evaluated three actual MMS-generated Kannada utterances, transmitted recovered native text and synthesized receiver audio. Standard reserved-token removal replaces the initial visible control-token decoding; no reference substitution, spelling correction or transliteration was used.
- Added explicit `ITANTRA_KANNADA_STT` selection, local safetensors loading, actionable missing-model errors, explicit download script and provider-specific verification evidence.
- Replaced “Fully supported” UI wording with “Round trip tested (synthetic)” and differentiated installed STT from absent TTS.
- Added exact process birth identities to startup records and a bounded legacy check. stop-dev targets recorded process IDs only; no broad process-name kill commands were used.
- Preserved the old report in `docs/archive/2026-10-12/VERIFICATION_REPORT.md`; updated README, speech/model/installation/demo/limitations docs and added `KANNADA_ASR.md` and `LANGUAGE_SUPPORT.md`.

## 3. Startup, health and Git

The existing start-dev/stop-dev scripts were exercised on verified project-owned processes. Backend and frontend started successfully; the health endpoint returned `{"status": "ok", "name": "iTantra", "version": "1.0.0", "simulation_mode": true}`. The frontend responded HTTP 200. Both services were running at the final report check. Startup waits for both endpoints and refuses occupied ports rather than terminating unrelated processes.

Git branch: **main**. **No commits, pushes or remote repositories** were created. Source remains untracked, matching the previous empty repository. Weights, `.env`, recordings, build outputs and temporary research results remain ignored.

```text
?? .dockerignore
?? .env.example
?? .github/
?? .gitignore
?? LICENSE
?? README.md
?? backend/
?? compose.yaml
?? datasets/
?? docs/
?? frontend/
?? infrastructure/
?? models/
?? ruff.toml
?? scripts/
```

## 4. Tests and regressions

- **44 backend tests passed**, zero failures/errors; raw JUnit: `research/results/resume-2026-10-13/backend-junit.xml`. The original 40 remain passing; four provider boundary/routing/evidence tests were added.
- **4 frontend unit tests passed**. TypeScript strict checking, Vite production build, Prettier check, Python compileall and Ruff passed.
- **10 full browser workflows passed in one run**, zero unexpected failures. JSON: `research/results/resume-2026-10-13/browser-tests.json`.
- **1 focused positive Kannada Speech Lab check passed**, including synthesized output playback and displayed actual CTC model identity. Log: `speech-lab-check.log`. This was a separate focused run, not falsely presented as part of the ten-workflow run.
- `npm audit` reported zero vulnerabilities. One non-failing Starlette/httpx TestClient deprecation warning remains. Docker runtime and Linux deployment were not executed.

The browser checks cover source upload, real A/B/C reconstruction and playback, microphone recording/pause/resume using synthetic capture, deliberate packet erasure, missing-model/invalid-audio feedback, recovered text retained on TTS failure, numerical charts, all nine routes at mobile width, Kannada semantic speech, actual compression comparison, analytics CSV export and local voice turns.

## 5. All nine pages

| Page | Verified behavior |
|---|---|
| Overview | Navigation to real studios/labs; conceptual diagram is labeled |
| Transceiver Studio | Actual upload → encode → packet/DSP → recover → decoded audio; measured results |
| Channel Simulation Lab | Real seeded BER/PER/recovery arrays and constellation charts |
| Multilingual Speech Lab | Actual native Kannada STT/TTS and output playback; missing-language TTS errors |
| Compression Comparison | Same source through real Opus and EnCodec, with two recovered outputs |
| Performance Analytics | Backend batch A/B/C results, measurement charts and actual CSV export |
| Live Demo | Actual encode/channel/decode voice turn and local conversation entry |
| Research & Architecture | Interactive explanatory stages and primary references; no fabricated measurement data |
| Experiment History | Actual SQLite-backed sessions, reopen/export/delete controls |

Research/overview are explanatory pages; their diagrams are not neural activation or physical RF measurements. Live Demo is turn-based software simulation.

## 6. Language/model status

| Language | Recognition | Synthesis | Full speech path |
|---|---|---|---|
| English | faster-whisper; synthetic sample tested | MMS tested | Synthetic round trip passed |
| Hindi | faster-whisper; synthetic sample tested | MMS tested | Synthetic round trip passed |
| Kannada | Vakyansh Kannada wav2vec2 CTC; synthetic sample tested | MMS tested | Synthetic round trip passed |
| Tamil | faster-whisper; checkpoint installed, language unverified | Not installed | Unavailable |
| Telugu | faster-whisper; checkpoint installed, language unverified | Not installed | Unavailable |
| Malayalam | faster-whisper; checkpoint installed, language unverified | Not installed | Unavailable |

All six scripts pass Unicode packet transport tests. That alone does not establish speech support. English/Hindi use local CPU int8 Whisper small. Kannada uses the public Kannada-specific CTC checkpoint. TTS uses MMS eng/hin/kan. EnCodec 24 kHz remains the installed neural codec; its four advertised operating points were round-trip verified previously and the current 3 kbps API/browser path was reverified. CPU PyTorch is available; CUDA is unavailable in this installation.

The official IndicConformer checkpoint was investigated but requires gated access/contact sharing and custom-code integration; it was not installed and no gate was bypassed. Vakyansh upstream lists MIT, but the converted HF checkpoint lacks an explicit model-card license. Model weights are not redistributed; resolve conversion redistribution terms separately. MMS and EnCodec weights retain CC-BY-NC-4.0 terms.

## 7. Actual transmission measurements

Fresh API checks used existing synthetic speech, ideal channel, BPSK, seed 42, default 256-byte packet payload and no repetition. Every listed result had CRC-valid payload recovery and a downloaded, finite, non-silent receiver waveform. Semantic sender and recovered text matched exactly; reference errors were measured separately.

| Run | Payload bytes | Total wire bits | Compute ms | Reference WER | Reference CER |
|---|---:|---:|---:|---:|---:|
| en-conventional | 6103 | 54776 | 892.57 | Not applicable | Not applicable |
| en-neural | 1533 | 13752 | 21402.83 | Not applicable | Not applicable |
| en-semantic | 83 | 912 | 16969.30 | 0.0 | 0.0 |
| hi-semantic | 107 | 1104 | 12827.05 | 0.8571428571428571 | 0.19444444444444445 |
| kn-semantic | 107 | 1104 | 9755.96 | 0.4 | 0.06060606060606061 |

These are individual samples and include actual metadata/headers/CRC. Computation may include cold model initialization and is not simulated airtime or real radio latency. Do not compare different language samples as population-level quality rankings.

Kannada CTC output evidence:

| Synthetic case | Actual recognized/recovered text | WER | CER |
|---|---|---:|---:|
| 1 | ನಮಸ್ಕಾರ ಇದು ನಮ್ಮ ಧ್ವನಿಯ ಪರೀಕ್ಷೆ | 0.4000 | 0.060606 |
| 2 | ನಮ್ಮ ರೇಡಿಯೋ ಸಂಪರ್ಕ ಉತ್ತಮವಾಗಿದೆ | 0.2500 | 0.032258 |
| 3 | ಇದು ಕನ್ನಡ ಭಾಷೆಯ ಧ್ವನಿ ಸಂದೇಶರ | 0.2000 | 0.035714 |

The first two omit punctuation; the third also adds a final character. Existing WER/CER rules use NFC, whitespace words and punctuation-sensitive codepoints. No human benchmark, punctuation normalization or hidden transcript repair was introduced. The previous Whisper wrong-script result is retained as historical evidence.

## 8. Charts and research results

`api-verification.json`, individual job JSON and receiver WAVs, `channel-sweep.json` and `verified-measurements.png` are under `research/results/resume-2026-10-13/`. The chart is generated from those actual arrays/results. The fresh AWGN sweep used eight trials per Es/N0 point. At 0 dB measured BER was 0.07856054 versus theoretical BPSK 0.07864960. A zero observed BER at higher SNR is a finite-sample observation, not proof of zero underlying error probability.

Prior `research/results/radio/` contains 2,640 saved AWGN/Rayleigh/repetition trials with CSV/JSON and graphs. `research/results/modes/` preserves the original four-SNR comparison. `research/results/latent/` preserves the actual 12-epoch PyTorch analog feature-channel training run, 331 train /93 validation /99 held-out patches and held-out MSE 0.301384 at 10 dB. It has floating-point latents, not a measured low-bitrate digital bitstream. No training results were recreated or invented during this continuation.

Fresh 100% packet-erasure verification returned failed recovery, no receiver audio and raw BER unavailable because no bits were comparable. Screenshots in `docs/screenshots/` show the actual interface and native Kannada receiver/Speech Lab results.

## 9. Exact PowerShell commands

Both services were running at report generation; open the existing app instead of launching a duplicate. To restart:

```powershell
Set-Location 'C:\Users\umesh\Desktop\projects\iTantra'
powershell -ExecutionPolicy Bypass -File scripts/stop-dev.ps1
powershell -ExecutionPolicy Bypass -File scripts/start-dev.ps1
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
```

Frontend: **http://127.0.0.1:5173**. Backend: **http://127.0.0.1:8000**. Swagger: **http://127.0.0.1:8000/docs**.

Separate foreground terminals: `powershell -ExecutionPolicy Bypass -File scripts/start-backend.ps1` and `powershell -ExecutionPolicy Bypass -File scripts/start-frontend.ps1`.

Tests: `powershell -ExecutionPolicy Bypass -File scripts/run-tests.ps1`; browser suite with servers up: `npm.cmd run test:e2e --prefix frontend -- --workers=1`. Latest API verification: `.venv/Scripts/python.exe -X utf8 scripts/resume-verification.py`. Plot: `.venv/Scripts/python.exe scripts/plot-resume-results.py`.

Current `.env` uses `ITANTRA_KANNADA_STT=vakyansh`. Fresh installations explicitly download with `.venv/Scripts/python.exe -X utf8 scripts/download-models.py --kannada-asr`, set that value and restart. `.env.example` preserves Whisper until this optional download is performed. Missing selected CTC weights produce an installation error without silent fallback.

## 10. Remaining limitations and next work

Tamil/Telugu/Malayalam synthesis checkpoints and complete-language validation remain pending. Human Kannada/Hindi/English accuracy and listening tests remain pending; Hindi still shows recognition errors. Greedy CTC does not restore punctuation and can make character/word errors. No physical SDR, measured RF throughput, learned adaptive policy, full-duplex streaming, ARQ/concealment, PESQ/STOI score or trained digital latent-bitstream transceiver exists. Perfect CSI and simulator-supplied packet boundaries remain explicit assumptions. A single missing packet conservatively fails the full encoded container. Cancellation is cooperative, media expires after 24 hours by default, and shared-source deletion affects other sessions. Local-first does not imply a secured public/LAN service; authentication is not implemented.

Prioritize licensed human-speech validation, the three missing synthesis providers, robust streaming/FEC/ARQ, and then a quantized digital research bottleneck or real SDR extension. No unresolved failure remains in the tested core workflows; broader requirements are limited as stated above.
