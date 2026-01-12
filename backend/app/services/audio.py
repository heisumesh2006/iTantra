import math
import subprocess
import numpy as np
from scipy.signal import resample_poly
import imageio_ffmpeg
from app.core.errors import ApplicationError


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
