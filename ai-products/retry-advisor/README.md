# Payment retry advisor

When a payment fails, should you retry it, wait, ask the customer, or stop? This project builds a small advisor for that decision and tests it against a fixed-timing baseline.

This is the first piece: a synthetic dataset. Everything here is invented. The failure mix and the retry odds are assumptions written in `generate.py`, so any result built on this data describes the simulator, not a real payment network.

## Generate the data

```
python generate.py 50000 7      # rows, seed
python -m unittest -q
```

Needs only the Python standard library. The output is `transactions.csv`, which is not committed: the seed makes it reproducible.

## What the simulator does

- 50,000 payment attempts over 30 days, split between card and UPI, across eight made-up issuers.
- A first-attempt failure rate per rail, which rises sharply during issuer outages (three 2-hour outages per issuer).
- Each failure gets a class, and one logged retry with a randomly assigned delay: 0, 5, 60, 360 or 1,440 minutes. Random assignment mimics a past A/B test, so the data can answer "what would waiting have done".
- Retry success depends on class and delay, and drops sharply if the issuer is still down at retry time.

## Data dictionary

| Column | Meaning |
|---|---|
| `txn_id` | Attempt id |
| `ts` | Attempt time |
| `rail` | `card` or `upi` |
| `issuer` | Made-up bank name |
| `amount_inr` | Amount, lognormal around INR 490 |
| `hour` | Hour of day of the attempt |
| `status` | `success` or `failed` |
| `failure_class` | `soft_decline`, `insufficient_funds`, `hard_decline`, `technical`, `auth_failed`, `pending_timeout`, `user_error` |
| `retry_delay_min` | Minutes before the logged retry (failed rows only) |
| `retry_success` | 1 if the retry succeeded |

How these classes relate to public decline codes is in the [failure taxonomy](../../research/payment-failure-taxonomy.md), once published.

## Limits

- The odds in `RETRY_P` are my assumptions, chosen to be plausible. They are not measured.
- No customer behaviour beyond the class label, no fees, no pending-payment double-debit modelling.
- Amounts are in rupees but the simulator carries no currency or country logic.
