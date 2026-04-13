"""Inference smoke checks with explicitly synthesized, non-human evaluation material."""

import json
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.db import store
from speech.providers import STT, TTS
from speech.registry import VERIFICATION
from app.schemas.requests import TransmissionRequest, ChannelConfig
from transceiver.pipeline import execute

store.initialize()
destination = ROOT / "research" / "results" / "smoke"
destination.mkdir(parents=True, exist_ok=True)
texts = {
    "en": "The radio link carries our voice across the network.",
    "hi": "नमस्ते। यह हमारी आवाज का परीक्षण है।",
    "kn": "ನಮಸ್ಕಾರ. ಇದು ನಮ್ಮ ಧ್ವನಿಯ ಪರೀಕ್ಷೆ.",
}
report = {
    "stt": [],
    "stt_model": str(__import__("speech.registry", fromlist=["stt_path"]).stt_path().name),
    "semantic_verified": [],
    "providers": {},
    "tts": [],
    "neural": False,
    "sample_source": "Meta MMS synthetic speech; no human corpus",
    "accuracy_validation": "Inference smoke checks only; synthetic self-evaluation is not a language benchmark.",
    "checks": [],
    "timestamp": store.now(),
}
for language, text in texts.items():
    try:
        started = time.perf_counter()
        waveform, rate, metadata = TTS.synthesize(text, language)
        assert len(waveform) > rate / 10 and np.isfinite(waveform).all() and np.std(waveform) > 0.001
        sf.write(destination / f"{language}-synthetic.wav", waveform, rate)
        report["tts"].append(language)
        entry = {
            "language": language,
            "source_text": text,
            "tts": metadata,
            "duration_seconds": len(waveform) / rate,
        }
        try:
            stt = STT.transcribe(waveform, rate, language)
            entry["stt"] = stt
            report["stt"].append(language)
            from speech.registry import selected_stt

            descriptor = selected_stt(language)
            report["providers"][language] = {
                "cache_key": descriptor["cache_key"],
                "model": stt["model"],
                "revision": stt.get("revision"),
                "native_script_verified": stt.get("native_script_observed", True),
                "roundtrip_verified": False,
            }
        except Exception as error:
            entry["stt_error"] = str(error)
        from app.services.audio import save

        media = save(waveform, rate, "synthetic_test_source")
        if language == "en":
            for mode in ("conventional", "neural", "semantic"):
                try:
                    result = execute(
                        TransmissionRequest(
                            media_id=media["id"],
                            language=language,
                            mode=mode,
                            reference=text,
                            channel_config=ChannelConfig(channel="ideal"),
                        )
                    )
                    assert result["recovery_status"] == "recovered" and result["receiver"]
                    (destination / f"{mode}-ideal.json").write_text(
                        json.dumps(result, ensure_ascii=False, indent=2),
                        encoding="utf-8",
                    )
                    entry[mode] = {"status": "passed", "metrics": result["metrics"]}
                    if mode == "neural":
                        report["neural"] = True
                    if mode == "semantic":
                        report["semantic_verified"].append(language)
                        report["providers"][language]["roundtrip_verified"] = True
                except Exception as error:
                    entry[mode] = {"status": "failed", "error": str(error)}
        elif language in report["stt"]:
            try:
                result = execute(
                    TransmissionRequest(
                        media_id=media["id"],
                        language=language,
                        mode="semantic",
                        reference=text,
                        channel_config=ChannelConfig(channel="awgn", snr_db=20),
                    )
                )
                assert result["recovery_status"] == "recovered" and result["receiver"]
                (destination / f"{language}-semantic.json").write_text(
                    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                entry["semantic"] = {"status": "passed", "metrics": result["metrics"]}
                report["semantic_verified"].append(language)
                report["providers"][language]["roundtrip_verified"] = True
            except Exception as error:
                entry["semantic"] = {"status": "failed", "error": str(error)}
        entry["wall_ms"] = (time.perf_counter() - started) * 1000
        report["checks"].append(entry)
        print(json.dumps(entry, ensure_ascii=False), flush=True)
    except Exception as error:
        report["checks"].append({"language": language, "error": str(error)})
        print(language, "failed:", repr(error), flush=True)
VERIFICATION.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
(destination / "verification.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
)
with store.connection() as db:
    db.execute(
        "INSERT OR REPLACE INTO model_metadata VALUES(?,?)",
        ("smoke-verification", json.dumps(report, ensure_ascii=False)),
    )
print("Verified STT:", report["stt"], "TTS:", report["tts"], "Neural:", report["neural"])
