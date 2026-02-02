from app.services.inference import INFERENCE_LOCK as MODEL_LOCK
from pathlib import Path
from datetime import datetime, timezone, timedelta
from uuid import UUID
from fastapi import APIRouter, UploadFile, Request
from fastapi.responses import FileResponse
from app.core.config import MAX_BYTES, RETENTION_HOURS
from app.core.errors import ApplicationError
from app.db import store
from app.schemas.requests import SynthesisRequest, TranscriptionRequest
from app.services import audio
from speech.registry import capabilities, languages
from speech.providers import STT, TTS

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
