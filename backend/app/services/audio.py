import subprocess
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
