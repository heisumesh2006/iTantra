from fastapi import APIRouter
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
