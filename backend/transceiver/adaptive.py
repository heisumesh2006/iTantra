from speech.registry import capabilities


def recommend(request) -> dict:
    cap = capabilities()
    language = next(entry for entry in cap["languages"] if entry["code"] == request.language)
    speech_ready = (
        language["stt_installed"]
        and language["tts_installed"]
        and language.get("roundtrip_verified", language["status"].startswith("Fully supported"))
    )
    if (
        request.objective == "meaning"
        and speech_ready
        and request.budget_kbps < 12
        and request.target_latency_ms >= 5000
    ):
        mode, reason = (
            "semantic",
            "Meaning is the objective, speech models are installed, and the budget is below the Opus target.",
        )
    elif cap["neural"]["installed"] and request.budget_kbps < 12:
        mode, reason = (
            "neural",
            "A compact neural representation fits the requested budget better than the 12 kbps waveform baseline.",
        )
    else:
        mode, reason = (
            "conventional",
            "Use the validated Opus baseline for waveform preservation or unavailable speech models.",
        )
    warnings = []
    if request.channel_config.snr_db < 8 or request.channel_config.erasure_rate > 0:
        warnings.append(
            "Poor channel: any missing packet fails whole-container recovery; consider repetition-3 or higher Es/N0."
        )
    if mode == "semantic":
        warnings.append(
            "STT errors propagate; speaker identity and prosody are not preserved. Confidence is unavailable."
        )
    warnings.append(
        "This is a recommendation; latency and wire budget are measured after processing, not guaranteed."
    )
    return {"mode": mode, "reason": reason, "tradeoffs": warnings, "policy": "explainable rules v1"}
