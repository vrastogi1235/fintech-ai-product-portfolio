"""Synthetic payment attempts with a logged retry for every failure.

Everything here is invented. The failure mix and retry odds are assumptions,
set in the tables below, so the analysis built on top of them describes this
simulator and not any real payment network.

Run: python generate.py [rows] [seed]  ->  transactions.csv
"""
import csv
import math
import random
import sys
from datetime import datetime, timedelta

START = datetime(2026, 1, 1)
DAYS = 30
ISSUERS = [f"Bank {c}" for c in "ABCDEFGH"]
DELAYS = [0, 5, 60, 360, 1440]  # minutes; assigned at random, like a past A/B test

# P(first attempt fails), by rail
FAIL_RATE = {"card": 0.09, "upi": 0.06}

# Share of failures by class, by rail
CLASS_MIX = {
    "card": {"soft_decline": 0.35, "insufficient_funds": 0.25, "hard_decline": 0.15,
             "technical": 0.15, "auth_failed": 0.10},
    "upi": {"technical": 0.40, "pending_timeout": 0.20, "insufficient_funds": 0.15,
            "user_error": 0.15, "soft_decline": 0.10},
}

# P(retry succeeds) by class and delay in minutes, when the issuer is healthy
RETRY_P = {
    "soft_decline": [0.12, 0.15, 0.28, 0.25, 0.20],
    "insufficient_funds": [0.02, 0.03, 0.05, 0.10, 0.25],
    "hard_decline": [0.01] * 5,
    "technical": [0.20, 0.35, 0.60, 0.65, 0.60],
    "auth_failed": [0.35, 0.35, 0.30, 0.20, 0.10],
    "pending_timeout": [0.10, 0.15, 0.30, 0.30, 0.25],
    "user_error": [0.50, 0.50, 0.45, 0.35, 0.25],
}


def downtime_windows(rng):
    """Three 2-hour outages per issuer, at random times."""
    span = DAYS * 24 * 60
    return {i: [START + timedelta(minutes=rng.randrange(span)) for _ in range(3)]
            for i in ISSUERS}


def is_down(windows, issuer, t):
    return any(w <= t < w + timedelta(hours=2) for w in windows[issuer])


def generate(rows=50_000, seed=7):
    rng = random.Random(seed)
    windows = downtime_windows(rng)
    out = []
    for n in range(rows):
        t = START + timedelta(minutes=rng.randrange(DAYS * 24 * 60))
        rail = "card" if rng.random() < 0.55 else "upi"
        issuer = rng.choice(ISSUERS)
        amount = round(math.exp(rng.gauss(6.2, 1.1)), 2)  # median about INR 490
        down = is_down(windows, issuer, t)
        row = {"txn_id": f"T{n:06d}", "ts": t.isoformat(timespec="minutes"),
               "rail": rail, "issuer": issuer, "amount_inr": amount,
               "hour": t.hour, "status": "success", "failure_class": "",
               "retry_delay_min": "", "retry_success": ""}
        if rng.random() < FAIL_RATE[rail] * (6 if down else 1):
            mix = CLASS_MIX["card" if rail == "card" else "upi"]
            cls = "technical" if down else rng.choices(list(mix), list(mix.values()))[0]
            delay = rng.choice(DELAYS)
            p = RETRY_P[cls][DELAYS.index(delay)]
            if is_down(windows, issuer, t + timedelta(minutes=delay)):
                p *= 0.2
            row.update(status="failed", failure_class=cls, retry_delay_min=delay,
                       retry_success=int(rng.random() < p))
        out.append(row)
    return out


if __name__ == "__main__":
    rows = int(sys.argv[1]) if len(sys.argv) > 1 else 50_000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    data = generate(rows, seed)
    with open("transactions.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(data[0]))
        w.writeheader()
        w.writerows(data)
    failed = sum(r["status"] == "failed" for r in data)
    print(f"wrote {len(data)} rows, {failed} failed ({failed / len(data):.1%})")
