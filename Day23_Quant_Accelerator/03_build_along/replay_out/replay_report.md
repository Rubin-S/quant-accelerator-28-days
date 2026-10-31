# Replay report: live pipeline vs backtest (IS 2008-09 → 2018-12, index stand-in)

| Test | Result | Pass? |
|---|---|---|
| 1 Parity: days where pipeline in/out ≠ engine | 0 of 2522 | PASS |
| 1 End equity gap vs engine | -29.0 bps (integer units + fee rounding) | PASS |
| 2 Limit orders at 09:30, ±0.25% off the open | 22 sent, 0 unfilled → first-try fill rate 100% | info |
| 2 Days the marketable-limit book is out of sync with the close-fill book | 0 | info |
| 2b PASSIVE limits at 09:30, −0.25% (trying to save the cushion) | 33 sent, 8 unfilled, 7 days out of sync | info |
| 3 Idempotence: orders when every day runs twice | 21 vs 21 | PASS |

| Book | CAGR | Vol | Max DD |
|---|---|---|---|
| Engine (Day 15) | 6.7% | 14.2% | -30.4% |
| Pipeline, close fills | 6.6% | 14.2% | -30.2% |
| Pipeline, 09:30 marketable limits | 6.7% | 14.2% | -30.1% |
| Pipeline, 09:30 passive limits | 6.3% | 14.3% | -30.1% |

Journals: journal_close.jsonl, journal_limit.jsonl (append-only JSONL, one line per event).