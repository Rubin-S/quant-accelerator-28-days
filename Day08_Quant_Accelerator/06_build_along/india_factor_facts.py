"""Context, not a trial: what do India's academic factor returns look like?
Source: IIMA Indian Fama-French-Momentum data library (Agarwalla, Jacob, Varma), release 2025-12,
survivorship-bias-adjusted monthly returns in %. These are long-short STOCK portfolios: you can't trade them
with ETFs and 1.0x, no shorting. Use them to calibrate what a "real" edge looks like: its size, its pain, its decay."""
import pandas as pd, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent
f = HERE.parent / "04_india_evidence" / "IIMA_factor_library_2025-12" / "2025-12_FourFactors_and_Market_Returns_Monthly_SurvivorshipBiasAdjusted.csv"
d = pd.read_csv(f, na_values="NA"); d["Date"] = pd.PeriodIndex(d["Date"], freq="M"); d = d.set_index("Date") / 100
d["MKT_RF"] = d["MF"] - d["RF"]
def stats(x):
    x = x.dropna(); ann = x.mean() * 12; vol = x.std() * np.sqrt(12); t = x.mean() / x.std() * np.sqrt(len(x))
    eq = (1 + x).cumprod(); dd = (eq / eq.cummax() - 1).min()
    return pd.Series({"ann_mean": ann, "ann_vol": vol, "sharpe": ann / vol, "t": t, "max_dd": dd, "months": len(x)})
print("Full sample:"); print(pd.DataFrame({k: stats(d[k]) for k in ["MKT_RF", "SMB", "HML", "WML"]}).T.round(3))
print("\nMomentum (WML) by era: does the edge shrink?")
for a, b in [("1994", "2004"), ("2005", "2014"), ("2015", "2025")]:
    s = stats(d.loc[a:b, "WML"]); print(f"  {a}-{b}: ann mean {s.ann_mean:6.1%}  sharpe {s.sharpe:4.2f}  t {s.t:4.1f}  max DD {s.max_dd:6.1%}")
print("\nQuestion: momentum is India's strongest factor here. Why can't we just trade it? (List 3 reasons: universe, shorting, turnover/costs.)")
