# %% [markdown]
# # Day 15 demo: engine v2 on the exploration window (2007-09 → 2018-12)
# Signal: NIFTY 50 close (reconciled to NSE on Day 14). Trade: the INDEX as a stand-in for NIFTYBEES, because Yahoo's
# NIFTYBEES failed the Day 14 audit. Swap in your NSE-rebuilt CSV via `load_frame(..., trade_csv=...)`.
# Cash: 6% flat is a PLACEHOLDER (Day 13 ruling: replace it with a real overnight/LIQUIDBEES series before Day 20).
# %%
import pandas as pd, numpy as np
from engine import load_frame, DataFeed, Engine, FaberMonthly, Constant, VolTargetSizer, CostModel, CashModel, metrics
df = load_frame("../06_data/NIFTY50_daily.csv", "../06_data/NIFTY50_daily.csv")
runs = {
    "buy & hold":                      dict(strategy=Constant(1.0)),
    "Faber 10m":                       dict(strategy=FaberMonthly()),
    "Faber 10m + vol target 12%":      dict(strategy=FaberMonthly(), sizer=VolTargetSizer(0.12)),
    "Faber 10m + vol 12% + 10% band":  dict(strategy=FaberMonthly(), sizer=VolTargetSizer(0.12), band=0.10),
    "Faber 10m, NO costs, cash 0%":    dict(strategy=FaberMonthly(), costs=CostModel(0, use_nse=False), cash=CashModel(0.0)),
}
rows = {}
for name, kw in runs.items():
    kw.setdefault("cash", CashModel(0.06)); res = Engine(DataFeed(df), **kw).run(); m = metrics(res.equity, rf=0.0 if kw["cash"].rate == 0 else 0.06)
    rows[name] = {**{k: round(v, 3) for k, v in m.items()}, "trades": len(res.trades), "costs_inr": round(res.total_costs),
                  "avg_exposure": round(res.weights.mean(), 2)}
out = pd.DataFrame(rows).T; print(out.to_string())
# The "vectorised v1" way: same-close fill, no costs, no cash — the number you'd have believed last week
r = df.trade_close.pct_change(); m = df.signal_close.resample("ME").last(); s = (m > m.rolling(10).mean()).astype(float)
v1 = (1 + s.reindex(df.index, method="ffill").shift(1).fillna(0) * r.fillna(0)).cumprod()
print("\nvectorised v1 (fill at the signal close, no frictions):", {k: round(v, 3) for k, v in metrics(v1).items()})
out.to_csv("demo_results.csv")
