# Engine v2: design in one page (read this before the code)

```
DataFeed ──bar t──▶ Strategy.on_bar ──weight──▶ VolTargetSizer ──target (≤1.0x)──▶ pending order
   ▲                                                                                      │
   │                                   next session t+1                                    ▼
   └── mark to market ◀── Portfolio (cash, units) ◀── fill at close t+1 ± slippage, NSE fees
```

| Component | One job | The leak or bug it prevents |
|---|---|---|
| DataFeed | hands out bars ≤ t only; `at(k>t)` raises | reading tomorrow (fails loudly, not silently) |
| Strategy | weight in [0,1] from data ≤ t | shorting, leverage from the signal |
| FaberMonthly | decides on the FIRST session of a new month | "is today month-end?" needs tomorrow's date |
| VolTargetSizer | EWMA(0.94) vol from returns ≤ t; cap 1.0 | levering up in calm markets (house rule) |
| CostModel | slippage per side + `nse_costs.leg_costs` | free trading; wrong-side slippage |
| CashModel | ACT/365 accrual on idle cash | a flat strategy earning 0% or a made-up rate |
| Engine | fill t−1's decision at t, then decide | same-bar fills; order-of-operations bugs |
| band | skip small re-sizes | daily churn: 1,184 vs 94 trades in the demo |

Order of operations each session (the most common bug source): interest → fill → mark → decide.
Swap any two and a test should fail. If none does, write the test.

Why event-driven when the strategy is monthly? Not for speed: for **the same code path in backtest and live**.
In Week 4 the DataFeed gets swapped for Kite's feed and the fill model for the paper-fill simulator. Nothing else should change.
