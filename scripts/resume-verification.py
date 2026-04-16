"""Verify real API outputs on synthetic speech and preserve prior research results."""

import io
import json
import sys
import time
from pathlib import Path
import numpy as np
import soundfile as sf
import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from speech.registry import VERIFICATION, selected_stt

sys.stdout.reconfigure(encoding="utf-8")
DEST = ROOT / "research/results/resume-2026-10-13"
DEST.mkdir(parents=True, exist_ok=True)
client = httpx.Client(base_url="http://127.0.0.1:8000/api/v1", timeout=240)


def request(method, path, **kwargs):
    response = client.request(method, path, **kwargs)
    response.raise_for_status()
    return response.json()


def wait_job(path):
    deadline = time.monotonic() + 300
    while time.monotonic() < deadline:
        job = request("GET", path)
        if job["status"] not in ("queued", "running"):
            assert job["status"] == "completed", job.get("error")
            return job
        time.sleep(0.3)
    raise RuntimeError("API job exceeded 300 seconds: " + path)


def validate_receiver(result, name):
    assert result["recovery_status"] == "recovered" and result["receiver"], result.get("reconstruction_error")
    response = client.get(result["receiver"]["url"].removeprefix("/api/v1"))
    response.raise_for_status()
    waveform, rate = sf.read(io.BytesIO(response.content), dtype="float32")
    assert np.isfinite(waveform).all() and np.std(waveform) > 0.001
    (DEST / (name + ".wav")).write_bytes(response.content)
    assert (
        result["metrics"]["payload_bytes"] > 0
        and result["metrics"]["total_transmitted_bits"] > result["metrics"]["payload_bits"]
    )
    assert result["metrics"]["raw_ber"] == 0
    if result["mode"] == "semantic":
        assert result["sender_text"] == result["recovered_text"]


texts = {
    "en": "The radio link carries our voice across the network.",
    "hi": "नमस्ते। यह हमारी आवाज का परीक्षण है।",
    "kn": "ನಮಸ್ಕಾರ. ಇದು ನಮ್ಮ ಧ್ವನಿಯ ಪರೀಕ್ಷೆ.",
}
report = {
    "sample_source": "synthetic Meta MMS speech; no human language-quality benchmark",
    "runs": [],
    "kannada_cases": [],
    "configuration": {"channel": "ideal", "seed": 42},
}
source_media = {}
for language in ("en", "hi", "kn"):
    raw = (ROOT / f"research/results/smoke/{language}-synthetic.wav").read_bytes()
    media = request("POST", "/audio", files={"file": (language + ".wav", raw, "audio/wav")})
    source_media[language] = media
    modes = ("conventional", "neural", "semantic") if language == "en" else ("semantic",)
    for mode in modes:
        job = request(
            "POST",
            "/transmissions",
            json={
                "media_id": media["id"],
                "language": language,
                "mode": mode,
                "reference": texts[language],
                "channel_config": {"channel": "ideal", "seed": 42},
            },
        )
        job = wait_job("/transmissions/" + job["id"])
        name = f"{language}-{mode}"
        result = job["result"]
        validate_receiver(result, name)
        (DEST / (name + ".json")).write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
        report["runs"].append(
            {
                "name": name,
                "job_id": job["id"],
                "metrics": result["metrics"],
                "stt": result.get("stt"),
                "receiver_text": result.get("recovered_text"),
            }
        )
        print(name, "passed", result.get("recovered_text"), flush=True)
        if language == "kn":
            assert (
                result["stt"]["native_script_observed"]
                and result["stt"]["provider"] == "Vakyansh Kannada wav2vec2 CTC"
            )
            report["kannada_cases"].append(
                {
                    "reference": texts["kn"],
                    "text": result["recovered_text"],
                    "wer": result["metrics"]["wer"],
                    "cer": result["metrics"]["cer"],
                    "roundtrip": True,
                }
            )
            kannada_stt = result["stt"]

for index, text in enumerate(["ನಮ್ಮ ರೇಡಿಯೋ ಸಂಪರ್ಕ ಉತ್ತಮವಾಗಿದೆ.", "ಇದು ಕನ್ನಡ ಭಾಷೆಯ ಧ್ವನಿ ಸಂದೇಶ."], 2):
    synthesized = request("POST", "/speech/synthesize", json={"language": "kn", "text": text})
    job = request(
        "POST",
        "/transmissions",
        json={
            "media_id": synthesized["media"]["id"],
            "language": "kn",
            "mode": "semantic",
            "reference": text,
            "channel_config": {"channel": "ideal", "seed": 42},
        },
    )
    job = wait_job("/transmissions/" + job["id"])
    result = job["result"]
    validate_receiver(result, f"kn-case-{index}")
    assert result["stt"]["native_script_observed"]
    (DEST / f"kn-case-{index}.json").write_text(
        json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report["kannada_cases"].append(
        {
            "reference": text,
            "text": result["recovered_text"],
            "wer": result["metrics"]["wer"],
            "cer": result["metrics"]["cer"],
            "roundtrip": True,
        }
    )
    print("Kannada case", index, "passed:", result["recovered_text"], flush=True)

# Merge model-specific evidence without overwriting the historical Whisper failures.
evidence = json.loads(VERIFICATION.read_text(encoding="utf-8"))
evidence.setdefault("providers", {})["kn"] = {
    "cache_key": selected_stt("kn")["cache_key"],
    "model": kannada_stt["model"],
    "revision": kannada_stt["revision"],
    "native_script_verified": True,
    "roundtrip_verified": True,
    "sample_count": len(report["kannada_cases"]),
    "sample_source": report["sample_source"],
    "quality_cases": report["kannada_cases"],
}
VERIFICATION.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")

lost = request(
    "POST",
    "/transmissions",
    json={
        "media_id": source_media["en"]["id"],
        "mode": "conventional",
        "channel_config": {"channel": "ideal", "erasure_rate": 1},
    },
)
lost = wait_job("/transmissions/" + lost["id"])
assert lost["result"]["recovery_status"] == "failed" and lost["result"]["receiver"] is None
assert lost["result"]["metrics"]["raw_ber"] is None
(DEST / "erasure-failure.json").write_text(json.dumps(lost, indent=2), encoding="utf-8")
report["erasure_failure_verified"] = True

sweep = request(
    "POST",
    "/channels/simulate",
    json={"config": {"channel": "awgn", "seed": 42}, "snr_values": [0, 4, 8, 12, 16], "trials": 8},
)
assert len(sweep["points"]) == 5 and sweep["constellation"]
(DEST / "channel-sweep.json").write_text(json.dumps(sweep, indent=2), encoding="utf-8")
report["channel_points"] = sweep["points"]
report["languages"] = request("GET", "/languages")
report["health"] = request("GET", "/health")
(DEST / "api-verification.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("API verification complete; actual receiver files and metrics saved.", flush=True)
