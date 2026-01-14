import json
import math
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from uuid import uuid4
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly, stft
import imageio_ffmpeg
from app.core.config import MEDIA, MAX_SECONDS, RETENTION_HOURS
from app.core.errors import ApplicationError
from app.db import store


def ffmpeg() -> str:
    return imageio_ffmpeg.get_ffmpeg_exe()


def run_ffmpeg(arguments: list[str]) -> None:
    try:
        subprocess.run(
            [ffmpeg(), "-hide_banner", "-loglevel", "error", "-nostdin", *arguments],
            check=True,
            capture_output=True,
            timeout=90,
        )
    except (subprocess.SubprocessError, OSError) as error:
        raise ApplicationError("FFmpeg could not decode or encode this audio", "audio_error") from error


def resample(audio, rate: int, target: int):
    divisor = math.gcd(rate, target)
    return (
        resample_poly(audio, target // divisor, rate // divisor).astype(np.float32)
        if rate != target
        else audio
    )


def load(identifier: str):
    entry = store.get_media(identifier)
    if entry is None or not Path(entry["path"]).is_file():
        raise ApplicationError("Media is missing or expired; upload it again", "media_missing", 404)
    data, rate = sf.read(entry["path"], dtype="float32", always_2d=True)
    return data.mean(axis=1), rate, json.loads(entry["metadata"])


def describe(audio, rate: int) -> dict:
    if len(audio) == 0 or not np.isfinite(audio).all():
        raise ApplicationError("Empty or invalid audio")
    if not 0.1 <= len(audio) / rate <= MAX_SECONDS:
        raise ApplicationError(f"Audio must be between 0.1 and {MAX_SECONDS} seconds")
    rms = float(np.sqrt(np.mean(audio**2)))
    peaks = [float(np.max(np.abs(chunk))) for chunk in np.array_split(audio, min(220, len(audio)))]
    frequencies, times, spectrum = stft(
        audio, rate, nperseg=min(256, len(audio)), noverlap=min(128, len(audio) // 2)
    )
    spectrum = 20 * np.log10(np.maximum(np.abs(spectrum), 1e-6))
    step = max(1, spectrum.shape[1] // 100)
    return {
        "sample_rate": rate,
        "channels": 1,
        "samples": len(audio),
        "duration_seconds": len(audio) / rate,
        "format": "PCM16 WAV",
        "rms": rms,
        "silent": rms < 0.001,
        "clipped_fraction": float(np.mean(np.abs(audio) >= 0.999)),
        "waveform": peaks,
        "spectrogram": {
            "values": spectrum[:, ::step].round(1).tolist(),
            "frequencies": frequencies.tolist(),
            "times": times[::step].tolist(),
        },
        "input_pcm_bits": len(audio) * 16,
    }


def save(audio, rate: int, role: str = "receiver") -> dict:
    audio = np.asarray(audio, dtype=np.float32).reshape(-1)
    metadata = describe(audio, rate)
    path = MEDIA / f"{uuid4()}.wav"
    sf.write(path, audio, rate, subtype="PCM_16")
    return store.register_media(path, {**metadata, "role": role})


def ingest(data: bytes, extension: str) -> dict:
    source = MEDIA / f"{uuid4()}{extension}"
    target = MEDIA / f"{uuid4()}.wav"
    source.write_bytes(data)
    try:
        # Local-file input only; exclude network protocols embedded in malicious media containers.
        run_ffmpeg(
            [
                "-protocol_whitelist",
                "file,pipe",
                "-y",
                "-i",
                str(source),
                "-t",
                str(MAX_SECONDS + 1),
                "-ac",
                "1",
                "-ar",
                "16000",
                str(target),
            ]
        )
        audio, rate = sf.read(target, dtype="float32")
        metadata = describe(audio, rate)
        original = store.register_media(
            source, {"role": "original_upload", "format": extension, "bytes": len(data)}
        )
        return store.register_media(
            target,
            {
                **metadata,
                "role": "source",
                "original_media_id": original["id"],
                "original_url": original["url"],
            },
        )
    except Exception:
        source.unlink(missing_ok=True)
        target.unlink(missing_ok=True)
        raise


def cleanup():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=RETENTION_HOURS)
    for entry in store.media_entries():
        if datetime.fromisoformat(entry["created_at"]) < cutoff:
            Path(entry["path"]).unlink(missing_ok=True)
            store.remove_media(entry["id"])
