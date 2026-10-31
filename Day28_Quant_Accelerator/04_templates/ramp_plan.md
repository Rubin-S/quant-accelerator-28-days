# Capital ramp: a canary, not a launch
Promotion is decided by the CALENDAR and the EVIDENCE, never right after a win or during a drawdown.

| Stage | Size | Minimum time | Promote when ALL hold | Demote to paper if ANY |
|---|---|---|---|---|
| 0 Paper | ₹0 | done (Week 4) | gonogo.py = GO: STAGE 1 ONLY | n/a |
| 1 Canary | 1 decision cycle at ≤ 25% of capital_at_risk | ≥ 3 months AND ≥ 2 real orders | 0 unexplained orders; book = broker every day; D1/D2 clean; slippage measured on every fill; no rule breaks | unexplained order, any rule break by you, residual > 5 bps unexplained |
| 2 Half | ≤ 50% | ≥ 6 more months | same + a written 6-month review vs pre-registered expectations | same + live DD beyond the 90% band you predicted (Day 20) |
| 3 Full | 100% of capital_at_risk, NEVER above | ongoing, yearly review | n/a | same; any change to rules → back to Stage 1 after the 48-h cooling-off |

Notes
- Trading costs are a fixed fee per order plus a percentage, so on a tiny Stage 1 size the fixed part weighs more. Use nse_costs.py to check that a 25% order isn't eaten by fixed fees; if it is, use the smallest size where costs are under 0.2% a side.
- Capital never grows from profits automatically. Raising capital_at_risk is a rulebook amendment (48 h cooling-off).
- MinTRL (gonogo.py): live returns won't mean anything statistically for years. Don't promote on returns; promote on clean operations.
