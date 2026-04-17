import json
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

directory = Path(__file__).resolve().parents[1] / "research/results/resume-2026-10-13"
data = json.loads((directory / "api-verification.json").read_text(encoding="utf-8"))
runs = [r for r in data["runs"] if r["name"].startswith("en-")]
fig, axes = plt.subplots(1, 3, figsize=(13, 4))
labels = [r["name"].removeprefix("en-") for r in runs]
axes[0].bar(
    labels,
    [r["metrics"]["effective_link_bitrate_bps"] for r in runs],
    color=["#198b85", "#725cc2", "#db8b39"],
)
axes[0].set_ylabel("Wire bits / original speech second (bps)")
axes[1].bar(labels, [r["metrics"]["total_ms"] for r in runs], color=["#198b85", "#725cc2", "#db8b39"])
axes[1].set_ylabel("Compute latency incl. model initialization (ms)")
points = data["channel_points"]
axes[2].plot([p["snr_db"] for p in points], [p["ber"] for p in points], "o-", label="Measured BER")
axes[2].plot(
    [p["snr_db"] for p in points], [p["theoretical_ber"] for p in points], "--", label="Uncoded BPSK theory"
)
axes[2].set(xlabel="Es/N0 (dB)", ylabel="BER (linear scale)")
axes[2].legend(fontsize=8)
for ax in axes:
    ax.grid(axis="y", alpha=0.25)
fig.suptitle(
    "Actual API measurements · one synthetic English source / ideal mode comparison"
    + chr(10)
    + "AWGN sweep is separate, 8 trials per point; zero observed errors are finite-sample observations",
    fontsize=10,
)
fig.tight_layout()
fig.savefig(directory / "verified-measurements.png", dpi=180)
print("Saved traceable measurement figure.")
