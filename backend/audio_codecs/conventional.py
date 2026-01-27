from pathlib import Path
from tempfile import TemporaryDirectory
import soundfile as sf
from app.services.audio import run_ffmpeg
from app.core.errors import ApplicationError

CODEC = "Opus / Ogg, mono 16 kHz, 12 kbps target, 20 ms frames, VBR off"


def encode(audio, sample_rate: int) -> bytes:
    with TemporaryDirectory() as directory:
        source, target = Path(directory) / "source.wav", Path(directory) / "encoded.ogg"
        sf.write(source, audio, sample_rate, subtype="PCM_16")
        run_ffmpeg(
            [
                "-y",
                "-i",
                str(source),
                "-c:a",
                "libopus",
                "-b:a",
                "12000",
                "-vbr",
                "off",
                "-application",
                "voip",
                "-frame_duration",
                "20",
                str(target),
            ]
        )
        payload = target.read_bytes()
    if not payload.startswith(b"OggS"):
        raise ApplicationError("Conventional codec returned an invalid container")
    return payload
