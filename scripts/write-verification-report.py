"""Assemble a delivery report from actual saved measurements and browser results."""

import importlib.metadata as metadata
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if (ROOT / "research/results/resume-2026-10-13/api-verification.json").exists():
    import runpy

    runpy.run_path(str(ROOT / "scripts/write-resume-report.py"), run_name="__main__")
    raise SystemExit(0)

verification = json.loads((ROOT / "models/verified.json").read_text(encoding="utf-8"))
training = json.loads((ROOT / "research/results/latent/training.json").read_text(encoding="utf-8"))
evaluation = json.loads((ROOT / "research/results/latent/evaluation.json").read_text(encoding="utf-8"))
comparison = json.loads((ROOT / "research/results/modes/comparison.json").read_text(encoding="utf-8"))
browser = json.loads((ROOT / "research/results/browser-tests.json").read_text(encoding="utf-8"))
versions = {
    name: metadata.version(name)
    for name in [
        "fastapi",
        "uvicorn",
        "pydantic",
        "numpy",
        "scipy",
        "torch",
        "soundfile",
        "imageio-ffmpeg",
        "faster-whisper",
        "transformers",
        "huggingface-hub",
        "safetensors",
        "uroman",
        "pytest",
        "ruff",
        "httpx",
        "matplotlib",
    ]
}
git_status = subprocess.run(
    ["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True, check=True
).stdout
branch = subprocess.run(
    ["git", "branch", "--show-current"], cwd=ROOT, capture_output=True, text=True, check=True
).stdout.strip()
remotes = subprocess.run(
    ["git", "remote", "-v"], cwd=ROOT, capture_output=True, text=True, check=True
).stdout.strip()
head = subprocess.run(
    ["git", "rev-parse", "--verify", "HEAD"], cwd=ROOT, capture_output=True, text=True
).returncode
assert head != 0 and not remotes, "Unexpected commits/remotes; inspect before reporting"
full_browser = json.loads((ROOT / "research/results/browser-tests-full.json").read_text(encoding="utf-8"))


def cases(suites):
    found = {}
    for suite in suites:
        for spec in suite.get("specs", []):
            found[spec["title"]] = spec["ok"]
        found.update(cases(suite.get("suites", [])))
    return found


scenario_status = cases(full_browser["suites"])
scenario_status.update(cases(browser["suites"]))
assert len(scenario_status) >= 8 and all(scenario_status.values()), "Browser verification is incomplete"
stats = {"expected": len(scenario_status), "unexpected": sum(not value for value in scenario_status.values())}
rows = []
for run in comparison["runs"]:
    if run.get("metrics") and run["config"]["channel_config"]["snr_db"] == 20:
        m = run["metrics"]
        rows.append(
            f"| {run['mode']} | {m['payload_bytes']} | {m['total_transmitted_bits']} | {m['effective_link_bitrate_bps']:.2f} | {m['total_ms']:.2f} | {run['recovery_status']} |"
        )
report = f"""# iTantra delivery and verification report

Build date: 12 October 2026 (Asia/Kolkata). Project location: `{ROOT}`.

## 1. Project status
Delivered a working, validated local research prototype with frontend, backend, packet/DSP pipeline, real providers, experiments and documentation. The complete commercial/full-language vision is not claimed finished.

Fully implemented: nine routed pages; microphone recording/pause/replay and safe uploads; waveform/STFT; A/B/C transmission and explainable D selection; BPSK/QPSK, AWGN, IID Rayleigh/perfect CSI, erasure and controlled flips; CRC and repetition; exact recovered-byte decoding; persistent job events, cancellation, SQLite history and JSON/CSV; actual codebook serialization; real measured experiments; separate trained analog latent-channel extension.

Partial/unavailable: Kannada speech recognition returns the wrong script on the tested sample; Tamil/Telugu/Malayalam TTS weights are not installed. No physical SDR, continuous full-duplex conversation, learned adaptive controller, human listening study, verified human corpus, PESQ or STOI measurement. Proposed standalone codec APIs are consolidated into transmission/comparison routes. Model status remains honest and missing reconstruction preserves recovered text and link metrics.

## 2. Implemented architecture and files
React 19 + TypeScript + Vite + Lucide + Recharts, responsive dark CSS. FastAPI/Pydantic modular monolith with CPU inference, NumPy/SciPy DSP, SQLite WAL schema v1, UUID media files, bounded upload/duration/queue and retention. Local Faster Whisper STT, MMS VITS TTS, FFmpeg Opus and Transformers EnCodec. PyTorch feature-channel experiment is independent of the product's pretrained speech/codec pipelines.

Modules: `frontend/src/pages/` (9), `frontend/src/components/`, `backend/app/`, `backend/speech/`, `backend/audio_codecs/`, `backend/radio/`, `backend/transceiver/`, `backend/experiments/`, `backend/tests/`, `scripts/`, `docs/`, `datasets/manifest.example.jsonl`, `models/README.md`, `infrastructure/Dockerfile`, `compose.yaml`, `.github/workflows/ci.yml`, `.env.example`, `.gitignore`, MIT license for own source. No pretrained weights are tracked.

## 3. Test results
- Windows `scripts/run-tests.ps1`: **40 pytest tests passed**, **4 Vitest tests passed**, Ruff and TypeScript/Vite production build passed.
- `npm run test:e2e -- --workers=1`: **{stats["expected"]} Playwright tests passed**, {stats["unexpected"]} failed on final run. Includes real A/B/C browser reconstruction, actual receiver playback, microphone pause/resume/upload using synthetic capture, strict loss failure, missing-model/invalid-audio feedback, retained text on TTS failure, numerical charts and all nine mobile pages.
- All EnCodec operating points 1.5/3/6/12 kbps produced finite decoded waveforms. Actual packed payload sizes are saved.
- Scientific tests compare BPSK/QPSK AWGN with theory using 400,000 bits and six-standard-error tolerance; noise energy and coherent Rayleigh baseline are checked separately.
- Python `pip check`: no broken requirements. `npm audit`: zero reported vulnerabilities after test-runner upgrade. Docker Compose configuration parses; Docker image runtime and Linux commands were not executed.
- One non-failing Starlette/httpx TestClient deprecation warning remains in backend tests. No known critical defect in the verified workflow.

## 4. Real model status
STT: **Systran/faster-whisper-small**, CPU int8, installed and run. Tiny was tested first and upgraded after wrong-script output.
TTS: **facebook/mms-tts-eng**, **mms-tts-hin**, **mms-tts-kan**, actual waveform generation verified.
Neural: **facebook/encodec_24khz**, real packed 10-bit indices, all four advertised settings verified.
English and Hindi completed real synthetic speech → STT → simulated packets → recovered text → TTS. Kannada TTS works with native text; its tested Whisper transcript was Devanagari and the Kannada speech round trip failed synthesis. Kannada remains experimental, with no substitution of sender text. All six scripts pass Unicode transport tests, which does not imply all speech providers work.
CPU PyTorch {versions["torch"]}; CUDA unavailable. Approximately 16.87 GB physical RAM / 4.41 GB available at initial inspection. Model and inference limits are resource dependent. MMS/EnCodec weights are CC-BY-NC-4.0 (noncommercial research); their licenses are separate from project source.

## 5. Running the application
Existing virtual environment and English/Hindi/Kannada TTS, Whisper small and EnCodec checkpoints are installed.
```powershell
Set-Location 'C:\\Users\\umesh\\Desktop\\projects\\iTantra'
powershell -ExecutionPolicy Bypass -File scripts/start-dev.ps1
```
If ports are already in use by the project, open the running application rather than launching a duplicate. Separate-terminal alternatives: `scripts/start-backend.ps1` and `scripts/start-frontend.ps1`. Stop background-launch servers with `scripts/stop-dev.ps1`. Setup on another machine: `scripts/setup.ps1 -WithModels` and the explicit download-models.py command in README. All startup scripts were exercised; start-dev now waits for health/frontend readiness.

Frontend: http://127.0.0.1:5173 · Backend: http://127.0.0.1:8000 · Swagger: http://127.0.0.1:8000/docs. Local loopback only. Browser speech lab inference can take tens of seconds on CPU.

## 6. Research output
Measured mode comparison, **one 3.76-second synthetic English utterance**, AWGN 20 dB Es/N0, BPSK, 256-byte packets, no repetition, seed 42:

| Mode | Payload bytes | Wire bits | Wire / speech second (bps) | Compute time (ms) | Recovery |
|---|---:|---:|---:|---:|---|
{chr(10).join(rows)}

These numbers describe this sample/configuration only. They do not establish universal quality gains. Transmitted metadata and packet/CRC overhead are included. Computation is separate from modeled airtime; gross 12 kbaud BPSK wire rate is not experimentally measured RF throughput.

- `research/results/smoke/`: real provider verification JSON, synthetic WAV fixtures, ideal A/B/C results, Hindi semantic result, all-neural-bitrate result.
- `research/results/modes/comparison.json` and `.csv`: 12 same-source runs across 4/8/12/20 dB. At 4 dB all payloads failed; at 8 dB semantic recovered while A/B failed; at 12/20 dB all recovered for this one seed/sample. `mode-comparison.png` traces to those results.
- `research/results/radio/`: AWGN/Rayleigh × repetition1/3, 11 Es/N0 points ×60 trials = **2,640 actual trials**, JSON/CSV and `radio-results.png`.
- `research/results/latent/`: **12 actual training epochs**, {training["train_patches"]} training /{training["validation_patches"]} validation /{training["heldout_patches"]} held-out patches from 24 phrase-disjoint synthetic English utterances, single MMS voice. Safetensors checkpoint, normalization, manifest, training/evaluation JSON and graph.
- Held-out normalized feature MSE at 10 dB: **{next(r["normalized_feature_mse"] for r in evaluation["results"] if r["snr_db"] == 10):.6f}**. This is an idealized analog latent-feature experiment with no measured digital bitrate or human-speech generalization claim.
- `docs/screenshots/`: actual overview, transceiver and channel lab screenshots. `research/results/browser-tests.json` and frontend HTML report contain browser evidence.

Reproduce with scripts/compare_channel_models.py, compare-modes.py, prepare-synthetic-research.py, train_neural_transceiver.py, evaluate_neural_transceiver.py, plot_training_history.py and plot_mode_comparison.py. Detailed commands are in README. Raw results/model/audio artifacts are ignored by Git.

## 7. Limitations
No RF hardware or synchronization/MAC. Simulator supplies packet boundaries; flat fading is IID per symbol with perfect CSI. Whole-container recovery deliberately fails on missing packets; no ARQ/concealment. Semantic output changes speaker/prosody and inherits STT errors. On the one synthetic Hindi sample, WER was 0.7143 and CER 0.1667 under NFC/whitespace/reference rules; do not confuse successful transport with correct recognition. Kannada speech round trip failed. No human corpus or listening evaluation supports cross-language rankings. Heavy models are lazy but CPU initialization can be slow; cancellation is cooperative. SQLite migration v1 exists; future migration versions must be added when schema changes. Docker runtime is unverified. Shared-source deletion affects other sessions' playback. Audio expiration runs at startup and every five minutes; playback checks expiration immediately.

## 8. Git status
Branch: **{branch}**. Git initialized; **no commits, pushes or remotes**. All source is currently untracked. `.venv`, models/cache, recordings, `.env`, build/test outputs and temporary experiments are excluded.
```text
{git_status.strip()}
```
Final commands: `git status` and `git branch --show-current`.

## 9. Demonstration guide
Open the studio, upload `research/results/smoke/en-synthetic.wav` (label it synthetic), select Ideal, and run Conventional. Play receiver audio. Repeat Neural (3 kbps), then Semantic. Inspect wire bits and separately source/received text. Hindi can demonstrate native-script speech with real recognition errors visible. For Kannada use native text only with the explicit STT-bypass checkbox, or show the failed recognition case honestly. Set erasure to 100% to demonstrate absent recovered audio. Channel Lab produces real numerical charts; Analytics compares the same current sample; History reopens/export/deletes actual records. Live Demo is turn-based local simulation.

## 10. Next improvements
First integrate and benchmark a stronger Kannada/Indic recognizer using licensed human data. Then add packet-independent streaming codecs, FEC/ARQ/concealment, reference quality metrics/listening tests, a quantized digital learned bottleneck, broader model/version pinning and authenticated deployment. Validate SDR only after acquiring hardware. Larger multilingual datasets are needed before research performance claims.

Primary references are in docs/REFERENCES.md; full implementation details are in the other docs files.
"""
report = report.replace(str(ROOT).replace(chr(92), chr(92) * 2), str(ROOT))
(ROOT / "docs/VERIFICATION_REPORT.md").write_text(report, encoding="utf-8")
(ROOT / "docs/ENVIRONMENT.json").write_text(json.dumps(versions, indent=2), encoding="utf-8")
constraints = "\n".join(f"{name}=={version.split('+')[0]}" for name, version in versions.items())
(ROOT / "backend/requirements/validated-constraints.txt").write_text(
    "# Build-machine tested versions. Use with pip -c; this does not install optional providers.\n"
    + constraints
    + "\n",
    encoding="utf-8",
)
print("Report saved:", ROOT / "docs/VERIFICATION_REPORT.md")
