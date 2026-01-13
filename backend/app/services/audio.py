import json
import math
import subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
import imageio_ffmpeg
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
