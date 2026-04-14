import sys
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from speech.providers import TTS
from experiments.neural_features import log_mel_patches

phrases = [
    "Please check the radio signal.",
    "The network is ready for a new message.",
    "Our laboratory measures every transmitted bit.",
    "A clear voice is important for communication.",
    "We are sending speech across a simulated channel.",
    "The receiver checks the packet before playback.",
    "The test uses a repeatable random seed.",
    "Noise may corrupt some of the transmitted information.",
    "The model runs locally on this computer.",
    "The waveform is encoded before transmission.",
    "The engineer compares three different communication methods.",
    "The semantic mode carries the recognized words.",
    "Good morning and welcome to the research laboratory.",
    "The channel can introduce fading and packet loss.",
    "This recording is generated synthetic speech.",
    "Please repeat the last radio message.",
    "We separate training phrases from validation phrases.",
    "The neural encoder creates a compact representation.",
    "The decoder reconstructs acoustic features.",
    "The experiment measures feature reconstruction error.",
    "Held out examples are reserved for the final evaluation.",
    "The demonstration does not use physical radio hardware.",
    "The system reports a failure when the payload is missing.",
    "Thank you for listening to our communication experiment.",
]
sets = {"train": [], "validation": [], "test": []}
manifest = []
for index, text in enumerate(phrases):
    split = "train" if index < 16 else "validation" if index < 20 else "test"
    audio, rate, _ = TTS.synthesize(text, "en")
    patches = log_mel_patches(audio, rate)
    sets[split].extend(patches)
    manifest.append(
        {
            "phrase": text,
            "split": split,
            "source": "facebook/mms-tts-eng synthetic speech",
            "speaker": "single synthetic voice",
            "patches": len(patches),
            "sample_rate": rate,
        }
    )
    print(index + 1, split, len(patches), flush=True)
destination = ROOT / "research" / "results" / "latent"
destination.mkdir(parents=True, exist_ok=True)
np.savez_compressed(
    destination / "features.npz",
    **{name: np.stack(values) for name, values in sets.items()},
)
(destination / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print("Phrase-disjoint splits; one synthetic voice. No claim of speaker generalization.")
