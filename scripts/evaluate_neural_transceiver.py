import json
import sys
from pathlib import Path
import numpy as np
import torch
from safetensors.torch import load_model

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from experiments.neural_features import NeuralTransceiver

directory = ROOT / "research/results/latent"
data = np.load(directory / "features.npz", allow_pickle=False)
norm = np.load(directory / "normalization.npz", allow_pickle=False)
x = torch.tensor((data["test"] - norm["mean"]) / norm["std"])
model = NeuralTransceiver()
load_model(model, str(directory / "model.safetensors"))
model.eval()
torch.set_num_threads(2)
results = []
with torch.no_grad():
    for snr in [0, 5, 10, 15, 20]:
        torch.manual_seed(2026)
        mse = torch.mean((model(x, snr) - x) ** 2).item()
        results.append({"snr_db": snr, "normalized_feature_mse": mse, "patch_count": len(x)})
report = {
    "kind": "analog latent simulation",
    "split": "held-out synthetic phrases, single TTS voice",
    "seed": 2026,
    "results": results,
    "digital_bitrate": None,
}
(directory / "evaluation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
