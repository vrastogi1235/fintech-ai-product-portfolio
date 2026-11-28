"""Recovery rates by failure class and retry delay.

Run: python analysis.py [transactions.csv]   (prints markdown tables)
Works on rows from generate.generate() or on the CSV it writes.
"""
import csv
import sys
from collections import defaultdict


def load(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["amount_inr"] = float(r["amount_inr"])
        r["hour"] = int(r["hour"])
        if r["status"] == "failed":
            r["retry_delay_min"] = int(r["retry_delay_min"])
            r["retry_success"] = int(r["retry_success"])
    return rows


def failure_rate_by_rail(rows):
    seen = defaultdict(lambda: [0, 0])
    for r in rows:
        seen[r["rail"]][0] += 1
        seen[r["rail"]][1] += r["status"] == "failed"
    return {rail: failed / total for rail, (total, failed) in seen.items()}


def recovery_table(rows):
    """(failure_class, delay_min) -> (attempts, recovery_rate)"""
    d = defaultdict(list)
    for r in rows:
        if r["status"] == "failed":
            d[(r["failure_class"], r["retry_delay_min"])].append(r["retry_success"])
    return {k: (len(v), sum(v) / len(v)) for k, v in d.items()}


def best_delay(table, failure_class):
    options = {delay: rate for (c, delay), (_, rate) in table.items() if c == failure_class}
    return max(options, key=options.get)


if __name__ == "__main__":
    rows = load(sys.argv[1] if len(sys.argv) > 1 else "transactions.csv")
    table = recovery_table(rows)
    classes = sorted({c for c, _ in table})
    delays = sorted({d for _, d in table})
    failed = [r for r in rows if r["status"] == "failed"]

    print("| Rail | Failure rate |\n|---|---|")
    for rail, rate in sorted(failure_rate_by_rail(rows).items()):
        print(f"| {rail} | {rate:.1%} |")

    print("\n| Failure class | Share of failures | " + " | ".join(f"{d} min" for d in delays)
          + " | Best delay |\n|---|---|" + "---|" * (len(delays) + 1))
    for c in classes:
        share = sum(r["failure_class"] == c for r in failed) / len(failed)
        cells = " | ".join(f"{table[(c, d)][1]:.0%}" for d in delays)
        print(f"| {c} | {share:.0%} | {cells} | {best_delay(table, c)} min |")
