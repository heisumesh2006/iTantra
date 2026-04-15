import json
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

directory = Path(__file__).resolve().parents[1] / "research/results/latent"
history = json.loads((directory / "training.json").read_text())["history"]
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot([r["epoch"] for r in history], [r["train_mse"] for r in history], label="Training")
ax.plot(
    [r["epoch"] for r in history],
    [r["validation_mse"] for r in history],
    label="Validation",
)
ax.set(
    xlabel="Epoch",
    ylabel="Normalized log-mel feature MSE",
    title="Idealized analog latent channel · synthetic speech",
)
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(directory / "training.png", dpi=180)
