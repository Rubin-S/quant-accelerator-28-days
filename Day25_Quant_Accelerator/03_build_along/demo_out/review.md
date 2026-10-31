# Session review

**Contract breaches: 0**  (clean)

| Date | Events | Orders | Drill | Halted | Equity | Problems |
|---|---|---|---|---|---|---|
| 2018-12-18 | 1 | 0 |  |  | 20,000 |  |
| 2018-12-19 | 1 | 0 |  |  | 20,000 |  |
| 2018-12-20 | 5 | 1 | yes |  | 19,986 |  |
| 2018-12-21 | 1 | 0 |  |  | 19,631 |  |
| 2018-12-24 | 1 | 0 |  |  |  | aborted: ['preflight'] (explained in incidents.md) |
| 2018-12-26 | 1 | 0 |  |  | 19,587 |  |
| 2018-12-27 | 3 | 0 |  | position mismatch after recovery: book 72 vs broker 77 | 19,677 | C5: position mismatch (explained in incidents.md) |
| 2018-12-28 | 1 | 0 |  |  | 19,821 |  |
| 2018-12-31 | 1 | 0 |  |  | 19,826 |  |

## Order path quality
| Date | Tag | Side | Fill | Decision close | Shortfall (bps) | vs limit (bps) | Fees ₹ |
|---|---|---|---|---|---|---|---|
| 2018-12-20 | F10181220B0 | BUY | 273.93 | 274.18 | -9.2 | -44.7 | 3.70 |

Shortfall > 0 = you paid more (buy) / got less (sell) than the decision-day close. Over 1 trade it's noise; it's a number to track, not to react to.

Alerts by level: {'INFO': 8, 'WARN': 2, 'CRIT': 3}