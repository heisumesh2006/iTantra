from app.services.inference import INFERENCE_LOCK as MODEL_LOCK
import csv
import io
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from uuid import UUID
from fastapi import APIRouter, UploadFile, Request
from fastapi.responses import FileResponse, Response
from app.core.config import MAX_BYTES, RETENTION_HOURS
from app.core.errors import ApplicationError
from app.db import store
from app.schemas.requests import (
    TransmissionRequest,
    ChannelSweepRequest,
    SynthesisRequest,
    TranscriptionRequest,
    ExperimentRequest,
)
from app.services import audio, jobs
from radio.channel import sweep
from speech.registry import capabilities, languages
from speech.providers import STT, TTS
from transceiver.adaptive import recommend

router = APIRouter(prefix="/api/v1")


@router.get("/health")
def health():
    return {"status": "ok", "name": "iTantra", "version": "1.0.0", "simulation_mode": True}


@router.get("/capabilities")
@router.get("/models")
def models():
    return capabilities()


@router.get("/languages")
def language_list():
    return languages()


@router.post("/audio", status_code=201)
async def upload(request: Request, file: UploadFile):
    declared = request.headers.get("content-length")
    if declared and int(declared) > MAX_BYTES + 65536:
        raise ApplicationError("Upload exceeds size limit", "upload_too_large", 413)
    extension = Path(file.filename or "").suffix.lower()
    if extension not in (".wav", ".mp3", ".ogg", ".webm", ".m4a", ".flac"):
        raise ApplicationError("Upload WAV, MP3, Ogg, WebM, M4A or FLAC audio")
    data = await file.read(MAX_BYTES + 1)
    await file.close()
    if not data or len(data) > MAX_BYTES:
        raise ApplicationError("Audio empty or exceeds upload limit", "upload_too_large", 413)
    # Run decoding outside the event loop.
    from starlette.concurrency import run_in_threadpool

    return await run_in_threadpool(audio.ingest, data, extension)


@router.get("/media/{identifier}")
def media(identifier: UUID):
    entry = store.get_media(str(identifier))
    if not entry or not Path(entry["path"]).is_file():
        raise ApplicationError("Media missing or expired", "media_missing", 404)
    if datetime.fromisoformat(entry["created_at"]) < datetime.now(timezone.utc) - timedelta(
        hours=RETENTION_HOURS
    ):
        Path(entry["path"]).unlink(missing_ok=True)
        store.remove_media(str(identifier))
        raise ApplicationError("Media expired", "media_missing", 404)
    return FileResponse(entry["path"], filename=f"itantra-{identifier}{Path(entry['path']).suffix}")


@router.post("/speech/transcribe")
def transcribe(request: TranscriptionRequest):
    with MODEL_LOCK:
        waveform, rate, _ = audio.load(str(request.media_id))
        return STT.transcribe(waveform, rate, request.language)


@router.post("/speech/synthesize")
def synthesize(request: SynthesisRequest):
    with MODEL_LOCK:
        waveform, rate, info = TTS.synthesize(request.text, request.language)
        return {"media": audio.save(waveform, rate), **info}


@router.post("/adaptive/recommend")
def adaptive(request: TransmissionRequest):
    return recommend(request)


@router.post("/transmissions", status_code=202)
def transmit(request: TransmissionRequest):
    if not request.media_id and request.text is None:
        raise ApplicationError("Provide audio or explicit semantic text")
    if request.text is not None and request.mode not in ("semantic", "adaptive"):
        raise ApplicationError("Manual text is available only for semantic mode")
    if request.media_id:
        audio.load(str(request.media_id))
    return jobs.submit("transmissions", request)


@router.get("/transmissions")
def transmissions():
    return store.list_jobs("transmissions")


def get_job(table, identifier):
    job = store.get_job(table, str(identifier))
    if not job:
        raise ApplicationError("Job not found", "not_found", 404)
    return job


@router.get("/transmissions/{identifier}")
@router.get("/transmissions/{identifier}/result")
def transmission(identifier: UUID):
    return get_job("transmissions", identifier)


@router.post("/transmissions/{identifier}/cancel")
@router.post("/experiments/{identifier}/cancel")
def cancel(identifier: UUID):
    return {
        "cancellation_requested": jobs.cancel(str(identifier)),
        "note": "Active inference stops at its next stage boundary",
    }


@router.delete("/transmissions/{identifier}")
def delete_transmission(identifier: UUID):
    job = get_job("transmissions", identifier)
    if job["status"] in ("queued", "running"):
        raise ApplicationError("Cancel and wait for processing before deleting", "job_active", 409)
    result = job.get("result") or {}
    media_ids = set()
    for entry in (result.get("source"), result.get("receiver")):
        if entry:
            media_ids.add(entry["id"])
            if entry.get("original_media_id"):
                media_ids.add(entry["original_media_id"])
    if job["config"].get("media_id"):
        media_ids.add(job["config"]["media_id"])
    for media_id in media_ids:
        entry = store.get_media(media_id)
        if entry:
            Path(entry["path"]).unlink(missing_ok=True)
            store.remove_media(media_id)
    with store.connection() as db:
        db.execute("DELETE FROM transmissions WHERE id=?", (str(identifier),))
    return {
        "deleted": str(identifier),
        "note": "Shared source media is also deleted; other sessions may need a fresh upload",
    }


@router.post("/channels/simulate")
def simulate(request: ChannelSweepRequest):
    return sweep(request)


@router.post("/experiments/run", status_code=202)
def experiment_run(request: ExperimentRequest):
    audio.load(str(request.media_id))
    return jobs.submit("experiments", request)


@router.get("/experiments")
def experiments():
    return store.list_jobs("experiments")


@router.get("/experiments/{identifier}")
def experiment(identifier: UUID):
    return get_job("experiments", identifier)


@router.get("/metrics/summary")
@router.get("/metrics/comparison")
def summary():
    records = [job for job in store.list_jobs("transmissions") if job["result"]]
    return {
        "count": len(records),
        "runs": [
            {
                "id": j["id"],
                "mode": j["result"]["mode"],
                "language": j["config"]["language"],
                "snr_db": j["config"]["channel_config"]["snr_db"],
                "status": j["result"]["recovery_status"],
                **j["result"]["metrics"],
            }
            for j in records
        ],
    }


@router.get("/exports/{table}/{identifier}")
def export(table: str, identifier: UUID, format: str = "json"):
    if table not in ("transmissions", "experiments") or format not in ("json", "csv"):
        raise ApplicationError("Invalid export format or collection")
    job = get_job(table, identifier)
    if format == "json":
        return Response(
            json.dumps(job, ensure_ascii=False, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{identifier}.json"'},
        )
    runs = (
        job["result"].get("runs", [])
        if table == "experiments" and job["result"]
        else [job["result"]]
        if job["result"]
        else []
    )
    rows = [
        {
            "mode": r.get("mode"),
            "snr_db": r.get("config", {}).get("channel_config", {}).get("snr_db", r.get("snr_db")),
            "status": r.get("recovery_status", r.get("status")),
            "error": r.get("error"),
            **r.get("metrics", {}),
        }
        for r in runs
    ]
    output = io.StringIO()
    if rows:
        columns = sorted(set().union(*(r.keys() for r in rows)))
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    return Response(
        output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{identifier}.csv"'},
    )
