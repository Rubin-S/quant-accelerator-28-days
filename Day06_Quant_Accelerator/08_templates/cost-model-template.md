# My cost model (fill from sources, never from memory)
Put this at the top of every backtest from Day 9 on. Run every backtest at BOTH the low and the high case.

| Component | Low case | High case | Source (URL + date checked) |
|---|---|---|---|
| Half-spread per side (bps) | 1 tick = ~0.4 bps | | Live Kite book, Day 13 |
| Brokerage per order | | | Your broker's charges page |
| STT / exchange txn / SEBI fee / stamp duty / GST | | | Broker's charges page + NSE circular |
| Impact (bps), our size | ~0 | | Square-root law estimate |
| Missed fills / chasing (bps) | | | Your paper-fill simulator, Week 4 |
| **All-in per round trip (bps)** | | | |

Max round trips/yr before costs eat half a 4% edge: low case __, high case __
