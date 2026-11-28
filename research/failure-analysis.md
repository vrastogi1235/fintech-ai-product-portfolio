# Failure analysis on the synthetic dataset

Data: 50,000 simulated attempts, seed 7, from `ai-products/retry-advisor/generate.py`. Reproduce with `python generate.py 50000 7` then `python analysis.py transactions.csv`.

One caution before the numbers. The simulator's retry odds are assumptions I wrote down, so the patterns below are what I put in, read back out. The value of this exercise is the method: checking that the analysis recovers the structure it should, before I trust it on anything else.

## Failure rate by rail

| Rail | Failure rate |
|---|---|
| card | 9.5% |
| upi | 6.3% |

Of 50,000 attempts, 4,036 failed (8.1%). Card is higher than its 9% base setting because issuer outages add failures.

## Recovery rate by failure class and retry delay

Each failed attempt has one logged retry with a randomly assigned delay, so these rates compare delays fairly.

| Failure class | Share of failures | 0 min | 5 min | 60 min | 360 min | 1440 min | Best delay |
|---|---|---|---|---|---|---|---|
| auth_failed | 6% | 28% | 48% | 37% | 23% | 12% | 5 min |
| hard_decline | 9% | 1% | 3% | 0% | 3% | 2% | 5 min |
| insufficient_funds | 20% | 5% | 2% | 4% | 10% | 23% | 1440 min |
| pending_timeout | 7% | 17% | 16% | 31% | 25% | 26% | 60 min |
| soft_decline | 26% | 13% | 19% | 28% | 23% | 16% | 60 min |
| technical | 27% | 19% | 29% | 61% | 66% | 63% | 360 min |
| user_error | 5% | 60% | 53% | 57% | 43% | 24% | 0 min |

## What stands out

1. Waiting matters most for technical failures. An immediate retry recovers 19%. An hour later it is 61%. After that the curve is flat, so 60 minutes captures nearly all the gain with a much shorter wait than 360.
2. Insufficient funds needs a day. 5% right away, 23% after 24 hours.
3. Hard declines never recover. Every delay is at or below 3%. The "best delay" of 5 minutes is noise: each cell holds about 70 to 90 attempts, so a 2-point gap means a couple of payments. A real advisor should not pick delays for this class at all.
4. Customer-driven classes favour speed. Wrong PIN and failed authentication recover best soon after the failure, while the customer is still on the page. In practice this is a prompt to the customer, not a silent retry.
5. Two-thirds of failures are three classes. Technical, soft decline and insufficient funds make up 73% of failures, so a policy for just those captures most of the opportunity.

## What this means for the advisor

- A fixed delay is a compromise. No single delay is best for every class, which is the case for a class-aware policy.
- The first decision is whether to retry at all. Skipping hard declines costs nothing here and saves retry volume.
- Small cells are dangerous. Choosing "best delay" from a table with a few dozen attempts per cell would fit noise. The next step builds the simplest rule set first and checks that each rule is backed by enough data.
