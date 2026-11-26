# Payment failure taxonomy: what each failure means for a retry decision

A retry advisor only works if "failed" is split into classes that call for different actions. This note builds that split from public documentation and maps it to the classes used in the [synthetic dataset](../ai-products/retry-advisor/README.md). Every claim links to the page I read. Where I could not read a primary source, I say so.

## Cards

Stripe says issuers label most declines generically, so the true reason is often hidden. It exposes two extra signals: a network decline code and a network advice code (Mastercard calls this the Merchant Advice Code). Its `advice_code` values are `do_not_try_again`, `try_again_later` and `confirm_card_data`. Source: [Stripe, card declines](https://docs.stripe.com/declines/card).

Stripe's [decline code guide](https://docs.stripe.com/declines/codes) groups codes by what to do next:

| Guidance | Example codes | Retry value |
|---|---|---|
| Retry the payment | `issuer_not_available`, `processing_error`, `reenter_transaction` | High, the cause is usually temporary |
| Customer must act or switch method | `insufficient_funds`, `expired_card`, `card_velocity_exceeded` | Low until something changes |
| Reason hidden by the issuer | `do_not_honor`, `generic_decline` | Unknown, treat carefully |
| Never reveal the reason | `fraudulent`, `lost_card`, `stolen_card` | None |
| Fix the input first | `incorrect_cvc`, `incorrect_number` | Only after correction |
| Needs authentication | `authentication_required` | Retry with 3DS, not blind |

Mastercard advice codes, as documented by [Checkout.com](https://www.checkout.com/docs/developer-resources/testing/codes/recommendation-codes): 01 needs updated information, 02 try again later, 03 do not retry, 21 payment cancelled, and 24 to 30 mean wait from one hour up to ten days.

Retry ceilings matter too. Stripe recommends at most eight retries per charge because extra attempts can look like fraud to issuers. PayPal's merchant guidance summarises Visa and Mastercard limits and fees ([PayPal](https://www.paypal.com/us/brc/article/avoid-excessive-retries-penalties)). That is a secondary source and says fees can change, so check the network rulebooks before building on the numbers.

## UPI

Razorpay's [UPI error table](https://razorpay.com/docs/errors/payments/upi) separates:

- bank or provider downtime (`bank_technical_error`) and gateway trouble (`gateway_technical_error`), where retrying later is reasonable;
- customer-side outcomes such as `insufficient_funds`, `payment_cancelled` and expired requests, where the customer has to act;
- `payment_declined` when the debit failed.

The page has no guidance for payments stuck in a pending state. My own reading is that a retry is safe only when no debit happened, and that unknown status needs a status check first. No source I read states this rule, so treat it as a hypothesis to test.

NPCI also classifies declines as technical or business, with published reduction targets. I could not load those pages, so I am not quoting numbers until I have read the circulars.

## Mapping to the simulator

| Simulator class | Real-world signals it stands in for |
|---|---|
| `soft_decline` | `try_again_later`, `issuer_not_available`, generic issuer declines |
| `insufficient_funds` | `insufficient_funds`, `withdrawal_count_limit_exceeded` |
| `hard_decline` | `do_not_try_again`, lost or stolen card |
| `technical` | `processing_error`, `bank_technical_error`, `gateway_technical_error` |
| `auth_failed` | `authentication_required` |
| `pending_timeout` | UPI timeouts with unknown debit status |
| `user_error` | wrong PIN, `invalid_vpa`, expired request |

## What this means for the product

1. Decline class decides the action before timing does: never retry a hard decline, wait for insufficient funds, retry technical failures soon.
2. The reason code is often too generic to trust alone, so any real advisor needs extra signals.
3. Retry volume is a cost and a risk, not only an opportunity.
4. Pending payments are the riskiest case and need their own rule.

Open question for later in this project: how much of the real recovery gain comes from timing, and how much from simply not retrying what cannot succeed?
