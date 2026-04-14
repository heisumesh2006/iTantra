import argparse
import json
import sys
from pathlib import Path
import numpy as np
import torch
from safetensors.torch import save_model

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from experiments.neural_features import NeuralTransceiver

parser = argparse.ArgumentParser()
parser.add_argument("--epochs", type=int, default=12)
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
args = parser.parse_args()
torch.manual_seed(args.seed)
np.random.seed(args.seed)
torch.set_num_threads(2)
if args.device == "cuda" and not torch.cuda.is_available():
    raise SystemExit("CUDA unavailable; use --device cpu")
directory = ROOT / "research/results/latent"
data = np.load(directory / "features.npz", allow_pickle=False)
train = data["train"]
validation = data["validation"]
mean = train.mean(0)
std = np.maximum(train.std(0), 0.1)
np.savez(directory / "normalization.npz", mean=mean, std=std)
x = torch.tensor((train - mean) / std, device=args.device)
v = torch.tensor((validation - mean) / std, device=args.device)
model = NeuralTransceiver().to(args.device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
history = []
best = float("inf")
for epoch in range(args.epochs):
    model.train()
    order = torch.randperm(len(x), device=args.device)
    total = 0.0
    for batch in order.split(32):
        optimizer.zero_grad()
        loss = torch.mean((model(x[batch], 10) - x[batch]) ** 2)
        loss.backward()
        optimizer.step()
        total += loss.item() * len(batch)
    model.eval()
    with torch.random.fork_rng(), torch.no_grad():
        torch.manual_seed(args.seed + 100)
        validation_loss = torch.mean((model(v, 10) - v) ** 2).item()
    history.append(
        {
            "epoch": epoch + 1,
            "train_mse": total / len(x),
            "validation_mse": validation_loss,
        }
    )
    if validation_loss < best:
        best = validation_loss
        save_model(model, str(directory / "model.safetensors"))
    print(history[-1], flush=True)
report = {
    "kind": "idealized analog real latent AWGN; NOT a digital codec",
    "seed": args.seed,
    "device": args.device,
    "train_patches": len(x),
    "validation_patches": len(v),
    "heldout_patches": len(data["test"]),
    "train_snr_db": 10,
    "latent_dimensions": 32,
    "history": history,
    "status": "trained on synthetic speech",
}
(directory / "training.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
