import json
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

directory = Path(__file__).resolve().parents[1] / "research/results/modes"
data = json.loads((directory / "comparison.json").read_text(encoding="utf-8"))
runs = [run for run in data["runs"] if run.get("metrics") and run["config"]["channel_config"]["snr_db"] == 20]
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
names = [r["mode"] for r in runs]
axes[0].bar(
    names, [r["metrics"]["effective_link_bitrate_bps"] for r in runs], color=["#208a85", "#7a5dc6", "#e28b39"]
)
axes[0].set_ylabel("Wire bits / source speech second (bps)")
axes[1].bar(names, [r["metrics"]["total_ms"] for r in runs], color=["#208a85", "#7a5dc6", "#e28b39"])
axes[1].set_ylabel("Wall-clock processing (ms)")
fig.suptitle(
    "One synthetic English sample · AWGN 20 dB Es/N0 · BPSK · seed 42\nNot a speech-quality or population-level language benchmark"
)
fig.tight_layout()
fig.savefig(directory / "mode-comparison.png", dpi=180)
