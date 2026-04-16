import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.db import store
from app.services.audio import ingest
from app.schemas.requests import TransmissionRequest, ChannelConfig
from transceiver.pipeline import execute

parser = argparse.ArgumentParser()
parser.add_argument("--audio", type=Path, required=True)
parser.add_argument("--language", choices=["en", "hi", "kn", "ta", "te", "ml"], default="en")
parser.add_argument("--reference")
parser.add_argument("--snrs", type=float, nargs="+", default=[4, 8, 12, 20])
parser.add_argument("--seed", type=int, default=42)
args = parser.parse_args()
store.initialize()
media = ingest(args.audio.read_bytes(), args.audio.suffix)
runs = []
for mode in ["conventional", "neural", "semantic"]:
    for snr in args.snrs:
        request = TransmissionRequest(
            media_id=media["id"],
            language=args.language,
            mode=mode,
            reference=args.reference,
            channel_config=ChannelConfig(snr_db=snr, seed=args.seed),
        )
        try:
            result = execute(request)
            runs.append(result)
            print(mode, snr, result["recovery_status"], flush=True)
        except Exception as error:
            runs.append(
                {
                    "mode": mode,
                    "snr_db": snr,
                    "error": str(error),
                    "status": "unavailable",
                }
            )
            print(mode, snr, str(error), flush=True)
destination = ROOT / "research/results/modes"
destination.mkdir(parents=True, exist_ok=True)
(destination / "comparison.json").write_text(
    json.dumps(
        {
            "source": str(args.audio),
            "language": args.language,
            "seed": args.seed,
            "runs": runs,
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)
rows = [
    {
        "mode": r["mode"],
        "snr_db": r.get("snr_db", r.get("config", {}).get("channel_config", {}).get("snr_db")),
        "status": r.get("recovery_status", r.get("status")),
        "error": r.get("error"),
        **r.get("metrics", {}),
    }
    for r in runs
]
with (destination / "comparison.csv").open("w", newline="", encoding="utf-8") as out:
    writer = csv.DictWriter(out, fieldnames=sorted(set().union(*(row.keys() for row in rows))))
    writer.writeheader()
    writer.writerows(rows)
