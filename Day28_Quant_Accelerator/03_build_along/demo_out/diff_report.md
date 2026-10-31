# Live vs backtest

Sessions compared: 25

## D1 Signal
| Decision day | Live | Recomputed on final data | Match |
|---|---|---|---|
| 2018-12-03 | 1 | 1 | ✅ |

## D2 Position
Days live ≠ backtest: 0 · explained by a labelled drill: 0 · **unexplained: 0**

## D3 Fills and D4 costs
| Date | Side | Qty | Fill | Close | Slip vs close (bps) | Excess over 5 bps assumption | Fee ₹ | Model fee ₹ | Drill |
|---|---|---|---|---|---|---|---|---|---|
| 2018-12-04 | BUY | 182 | 109.06 | 109.00 | +5.0 | +0.0 | 3.72 | 3.72 |  |

**Slippage verdict (graduation test: mean excess over the 5 bps assumption ≤ 5 bps, upper 95% bound): UNDECIDED (1 fill)**  n = 1

## D5 Return attribution (fractions of starting equity)
| Piece | Value |
|---|---|
| live | -0.301% |
| backtest_index | -0.064% |
| timing_and_sizing | +0.001% |
| etf_vs_index | -0.170% |
| slippage | -0.050% |
| fees | -0.019% |
| residual | +0.000% |

Read it as: live = backtest(index) + timing + ETF-vs-index + slippage + fees + residual. A residual bigger than a few bps means the books don't add up: find it before Day 28.