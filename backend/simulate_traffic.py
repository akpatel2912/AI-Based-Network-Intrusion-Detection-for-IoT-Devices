"""Sends real rows from the dataset to the API, one at a time, so the dashboard fills up live.

Usage (API must be running):
    python simulate_traffic.py                    # 200 requests, 1 per second
    python simulate_traffic.py --count 50 --interval 0.5 --attack-ratio 0.4
"""
import argparse
import random
import time
from pathlib import Path
import httpx
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "ml" / "data" / "processed" / "processed_data.csv"

ap = argparse.ArgumentParser()
ap.add_argument("--url", default="http://127.0.0.1:8000")
ap.add_argument("--count", type=int, default=200)
ap.add_argument("--interval", type=float, default=1.0)
ap.add_argument("--attack-ratio", type=float, default=0.4)
args = ap.parse_args()

if not DATA.exists():
    raise SystemExit("processed_data.csv not found. Run 'python preprocess.py' in ml/src first.")
df = pd.read_csv(DATA)
normal, attack = df[df.sub_label == 0], df[df.sub_label == 1]
correct = 0
with httpx.Client(timeout=10) as client:
    for i in range(1, args.count + 1):
        row = (attack if random.random() < args.attack_ratio else normal).sample(1).iloc[0]
        truth = "Attack" if row["sub_label"] == 1 else "Normal"
        body = row.drop("sub_label").to_dict()
        try:
            resp = client.post(f"{args.url}/predict", json=body)
        except httpx.ConnectError:
            raise SystemExit(f"Cannot connect to {args.url}. Start the API first: uvicorn app.main:app --port 8000")
        if resp.status_code != 200:
            raise SystemExit(f"API returned {resp.status_code}: {resp.text[:200]}")
        res = resp.json()
        correct += res["prediction"] == truth
        print(f"[{i}/{args.count}] actual={truth:6} predicted={res['prediction']:6} confidence={res['confidence']}")
        time.sleep(args.interval)
print(f"Matched the true label on {correct}/{args.count} rows")
