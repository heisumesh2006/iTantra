from pathlib import Path
from fastapi import APIRouter, UploadFile, Request
from app.core.config import MAX_BYTES
from app.core.errors import ApplicationError
from app.services import audio
from speech.registry import capabilities, languages

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
