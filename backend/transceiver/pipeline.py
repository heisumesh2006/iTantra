import time
from uuid import uuid4
from app.core.errors import ApplicationError
from app.services import audio
from app.services.metrics import text_scores, si_sdr
from audio_codecs import conventional, neural, semantic
from radio.channel import transport
from speech.providers import STT, TTS
from transceiver.adaptive import recommend


def _execute(request, stage=lambda name, detail=None: None, cancelled=lambda: False):
    start = time.perf_counter()
    timing = {}

    def finish(name, since):
        timing[name] = (time.perf_counter() - since) * 1000

    def checkpoint(name, detail=None):
        if cancelled():
            raise ApplicationError("Cancelled; active model call completed before stopping", "cancelled", 409)
        stage(name, detail)

    checkpoint("Preparing audio")
    since = time.perf_counter()
    source, rate, source_meta = (None, None, None)
    if request.media_id:
        source, rate, source_meta = audio.load(str(request.media_id))
    decision = recommend(request) if request.mode == "adaptive" else None
    mode = decision["mode"] if decision else request.mode
    if mode != "semantic" and source is None:
        raise ApplicationError("Audio input is required for conventional and neural modes")
    finish("preprocessing_ms", since)
    checkpoint("Running encoder")
    since = time.perf_counter()
    transcript, stt, tts = None, None, None
    if mode == "conventional":
        payload = conventional.encode(source, rate)
        provider = conventional.CODEC
    elif mode == "neural":
        payload = neural.encode(source, rate, request.bandwidth_kbps)
        provider = "facebook/encodec_24khz (10-bit packed quantizer indices)"
    else:
        if request.text is not None:
            transcript = semantic.normalize(request.text)
            input_method = "Manual text; STT bypass explicitly requested"
        elif source is not None:
            stt = STT.transcribe(source, rate, request.language)
            transcript = semantic.normalize(stt["text"])
            input_method = "Speech recognition"
        else:
            raise ApplicationError("Semantic mode requires audio or explicit text")
        payload = semantic.encode(transcript, request.language)
        provider = "UTF-8 NFC JSON; optional zlib"
    finish("encoding_ms", since)
    checkpoint("Payload created", {"payload_bytes": len(payload)})
    checkpoint("Simulating packet, modulation and channel chain")
    link = transport(payload, uuid4(), mode, request.language, request.channel_config, cancelled)
    checkpoint(
        "Channel completed", {"packets_delivered": sum(p["status"] == "delivered" for p in link["packets"])}
    )
    recovered = link.pop("payload")
    recovered_text, receiver = None, None
    since = time.perf_counter()
    reconstruction_error = None
    if recovered is not None:
        try:
            checkpoint("Decoding recovered payload")
            if mode == "conventional":
                reconstructed, out_rate = conventional.decode(recovered)
            elif mode == "neural":
                reconstructed, out_rate = neural.decode(recovered)
            else:
                decoded = semantic.decode(recovered)
                if decoded["language"] != request.language:
                    raise ApplicationError("Recovered language does not match packet metadata")
                recovered_text = decoded["text"]
                reconstructed, out_rate, tts = TTS.synthesize(recovered_text, decoded["language"])
            checkpoint("Receiver audio generated")
            receiver = audio.save(reconstructed, out_rate)
        except ApplicationError as error:
            if error.code == "cancelled":
                raise
            reconstruction_error = error.message
            checkpoint("Receiver reconstruction failed", {"error": error.message})
    finish("decoding_ms", since)
    checkpoint("Calculating metrics")
    duration = source_meta["duration_seconds"] if source_meta else None
    metrics = link["metrics"]
    metrics.update(
        {
            "input_bits": source_meta["input_pcm_bits"]
            if source_meta
            else len(transcript.encode("utf-8")) * 8,
            "payload_bytes": len(payload),
            "source_bitrate_bps": len(payload) * 8 / duration if duration else None,
            "effective_link_bitrate_bps": metrics["total_transmitted_bits"] / duration if duration else None,
            "compression_ratio": source_meta["input_pcm_bits"] / (len(payload) * 8) if source_meta else None,
            "speech_duration_seconds": duration,
            "total_ms": (time.perf_counter() - start) * 1000,
            "si_sdr_db": si_sdr(source, audio.resample(reconstructed, out_rate, rate))
            if receiver and mode != "semantic"
            else None,
            "transcript_exact_match": transcript == recovered_text if recovered_text is not None else None,
            "budget_exceeded": metrics["total_transmitted_bits"] / duration > request.budget_kbps * 1000
            if duration
            else None,
            "latency_target_exceeded": (time.perf_counter() - start) * 1000 > request.target_latency_ms,
            "stoi": None,
            "pesq": None,
            **text_scores(request.reference, transcript if mode == "semantic" else None),
        }
    )
    return {
        "mode": mode,
        "provider": provider,
        "decision": decision,
        "source": source_meta,
        "receiver": receiver,
        "reconstruction_error": reconstruction_error,
        "reconstruction_status": "completed"
        if receiver
        else "failed"
        if recovered is not None
        else "not_attempted",
        "sender_text": transcript,
        "recovered_text": recovered_text,
        "stt": stt,
        "tts": tts,
        "semantic_input": input_method if mode == "semantic" else None,
        "recovery_status": "recovered" if recovered is not None else "failed",
        "config": request.model_dump(mode="json"),
        "timing": timing,
        **link,
    }
