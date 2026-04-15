import csv
import json
import sys
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.schemas.requests import ChannelSweepRequest, ChannelConfig
from radio.channel import sweep

destination = ROOT / "research/results/radio"
destination.mkdir(parents=True, exist_ok=True)
all_results = {}
for channel in ["awgn", "rayleigh"]:
    for repetition in [1, 3]:
        name = f"{channel}-repetition-{repetition}"
        data = sweep(
            ChannelSweepRequest(
                config=ChannelConfig(channel=channel, repetition=repetition),
                trials=60,
                snr_values=[-4, -2, 0, 2, 4, 6, 8, 10, 12, 16, 20],
            )
        )
        (destination / f"{name}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        with (destination / f"{name}.csv").open("w", newline="", encoding="utf-8") as out:
            writer = csv.DictWriter(out, fieldnames=list(data["points"][0]))
            writer.writeheader()
            writer.writerows(data["points"])
        all_results[name] = data
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for name, data in all_results.items():
    p = data["points"]
    axes[0].semilogy(
        [r["snr_db"] for r in p],
        [r["ber"] if r["ber"] else float("nan") for r in p],
        marker="o",
        label=name,
    )
    axes[1].plot(
        [r["snr_db"] for r in p],
        [r["recovery_rate"] for r in p],
        marker="o",
        label=name,
    )
reference = all_results["awgn-repetition-1"]["points"]
axes[0].semilogy(
    [p["snr_db"] for p in reference],
    [p["theoretical_ber"] for p in reference],
    "k--",
    label="Uncoded BPSK theory",
)
axes[0].set_ylabel("Raw coded-bit BER (erasures excluded)")
axes[1].set_ylabel("Complete payload recovery rate")
for ax in axes:
    ax.set_xlabel("Es/N0 (dB)")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7)
fig.suptitle("Seed 42–101 · 1,024-byte payloads · 256-byte packets · BPSK · 60 trials / point")
fig.tight_layout()
fig.savefig(destination / "radio-results.png", dpi=200)
print("Saved measured radio comparisons in", destination)
