"""Cross-check: my 40-line stationary bootstrap vs Kevin Sheppard's `arch` package (pip install arch).
Two independent implementations should give similar 90% Sharpe bands. If they don't, one of them is wrong."""
import math, numpy as np, pandas as pd
from arch.bootstrap import StationaryBootstrap, optimal_block_length
from engine import load_frame, DataFeed, Engine, FaberMonthly, VolTargetSizer, CostModel, CashModel
from is_report import cash_series, boot, common_start, GateUntil

df = load_frame("../06_data/NIFTY50_daily_IS_to_2018-12-31.csv", "../06_data/NIFTY50_daily_IS_to_2018-12-31.csv")
cash = CashModel(cash_series("../06_data/india_cash_rate_monthly_2007_2018.csv")); t0 = common_start(df, 12)
eq = Engine(DataFeed(df), GateUntil(FaberMonthly(10), t0), VolTargetSizer(None), CostModel(), cash).run().equity.loc[t0:]
r = eq.pct_change().dropna()
c = pd.Series([cash.growth(a, b) - 1 for a, b in zip(r.index.insert(0, eq.index[0])[:-1], r.index)], index=r.index)
x = (r - c).values
sr = lambda v: np.array([v.mean() / v.std(ddof=1) * math.sqrt(252)])
print("optimal mean block length (Politis-White):", optimal_block_length(x ** 2).loc[0, "stationary"].round(1))
bs = StationaryBootstrap(20, x, seed=17)
print("arch percentile 90% band:", bs.conf_int(sr, 2000, method="percentile", size=0.90).ravel().round(2))
mine = boot(pd.DataFrame({"p": r}), c, "p", 2000, 20)["p"]["sharpe_xs_90ci"]
print("is_report.py 90% band:   ", np.round(mine, 2))
