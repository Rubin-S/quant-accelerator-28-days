# %% [markdown]
# # Day 11 build-along: THE 8-POINT CHECKLIST SCORER
# Runs the paper checklist on the Day 10 survivors with numbers, using EXPLORATION data only (to 2018-12-31).
# The 2019+ data stays locked.
#
# Survivors tested here: (A) Faber 10-month SMA filter, (B) 12-month time-series trend, both on NIFTY 50, monthly,
# long or cash. (C) The momentum ETF can't be tested here: no such ETF traded before 2022. That's a finding, see P5.
#
# The 8 points: P1 payer, P2 costs ≥ 2–3x, P3 capacity, P4 not hidden beta, P5 enough bets, P6 bad regimes,
# P7 simple, P8 executable.
# P1 and P7 are judgement calls; the script prints the facts you need, and YOU write the verdict.

# %%
import numpy as np, pandas as pd
from pathlib import Path
from nse_costs import round_trip
HERE = Path(__file__).resolve().parent if "__file__" in globals() else Path(".")
DATA = HERE.parent / "09_data"
END, CASH = "2018-12-31", 0.06                      # exploration end; assumed cash yield (Day 9 caveat)
COST = round_trip(1e5, 1e5, "delivery", "etf_equity")["total"] / 1e5 + 2 * 0.0005   # ≈13.9 bps round trip

px = pd.read_csv(DATA / "NIFTY50_daily.csv", parse_dates=["Date"], index_col="Date")
px = px.loc[:END, ["Open", "Close"]].dropna()
beesd = pd.read_csv(DATA / "NIFTYBEES_daily.csv", parse_dates=["Date"], index_col="Date").loc[:END]
ff = pd.read_csv(DATA / "IIMA_FourFactors_Monthly_SurvivorshipAdjusted_2025-12.csv", na_values="NA")
ff.index = pd.PeriodIndex(ff.Date, freq="M"); ff = ff.drop(columns="Date") / 100   # MF = market minus RF

m_close = px.Close.resample("ME").last()
m_ret = m_close.pct_change()
cash_m = (1 + CASH) ** (1 / 12) - 1

def signals():
    return {"A Faber 10m SMA": (m_close > m_close.rolling(10).mean()).astype(int),
            "B 12m trend": (m_close.pct_change(12) > CASH).astype(int)}   # beat cash over 12 months

def run(sig, lag_days=1):
    """Monthly signal at month-end close. lag_days=0 assumes you traded AT that close (not executable, see P8).
    lag_days=1 trades at the next day's close instead."""
    d = px.Close.pct_change()
    pos_d = sig.reindex(px.index, method="ffill").shift(1 + lag_days).fillna(0)   # +1: signal known at close t
    if lag_days == 0:
        pos_d = sig.reindex(px.index, method="ffill").shift(1).fillna(0)
    cash_d = (1 + CASH) ** (1 / 245) - 1
    switches = pos_d.diff().abs().fillna(0)
    r = pos_d * d + (1 - pos_d) * cash_d - switches * COST / 2
    return r, pos_d, int(switches.sum())

def stats(r):
    r = r.dropna(); yrs = len(r) / 245
    cagr = (1 + r).prod() ** (1 / yrs) - 1; vol = r.std() * np.sqrt(245)
    dd = ((1 + r).cumprod() / (1 + r).cumprod().cummax() - 1).min()
    return cagr, vol, dd

START = "2008-07-01"      # after the 12-month lookback warms up (same start as Day 9)
bh = px.Close.pct_change().loc[START:]
print(f"Exploration window {START} to {END}. Round-trip cost used: {COST*1e4:.1f} bps. Cash {CASH:.0%} (assumed).\n")
c, v, d = stats(bh); print(f"Buy & hold NIFTY: CAGR {c:6.2%}  vol {v:6.2%}  maxDD {d:7.2%}\n")

for name, sig in signals().items():
    print("=" * 88); print(name)
    r, pos, n_sw = run(sig); r = r.loc[START:]; pos = pos.loc[START:]
    c, v, d = stats(r)
    print(f"  Net: CAGR {c:6.2%}  vol {v:6.2%}  maxDD {d:7.2%}   switches {n_sw}   time in market {pos.mean():.0%}")

    # P2 costs: average gain per in-market spell vs cost
    spell = (pos.diff() != 0).cumsum()[pos == 1]
    spell_ret = (1 + px.Close.pct_change().loc[START:][pos == 1]).groupby(spell).prod() - 1
    edge = spell_ret.mean()
    print(f"  P2 costs: {len(spell_ret)} spells, mean gain per spell {edge:.2%} vs round trip {COST:.2%} "
          f"-> {edge/COST:.0f}x cost  (mean is skewed by a few big trends; median {spell_ret.median():.2%})")

    # P3 capacity: NIFTYBEES traded value in 2018
    adv = (beesd.Close * beesd.Volume).loc["2018"].median()
    print(f"  P3 capacity: NIFTYBEES median daily traded value 2018 ≈ Rs {adv/1e7:.1f} cr; "
          f"1% of that ≈ Rs {adv*0.01/1e5:.0f} lakh per day")

    # P4 hidden beta: monthly regression on IIMA factors
    rm = (1 + r).resample("ME").prod() - 1; rm.index = rm.index.to_period("M")
    j = pd.concat([rm.rename("S"), ff], axis=1).dropna()
    y = j.S - j.RF
    for cols in (["MF"], ["MF", "SMB", "HML", "WML"]):
        X = np.column_stack([np.ones(len(j))] + [j[c].values for c in cols])
        b, *_ = np.linalg.lstsq(X, y.values, rcond=None)
        res = y.values - X @ b; s2 = res @ res / (len(y) - X.shape[1])
        se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
        tag = " + ".join(cols)
        print(f"  P4 on [{tag}]: alpha {b[0]*12:+.2%}/yr (t {b[0]/se[0]:+.2f}); "
              + ", ".join(f"{c} beta {b[i+1]:+.2f}" for i, c in enumerate(cols)))

    # P5 enough bets
    months = len(rm.dropna())
    print(f"  P5 bets: {months} monthly returns, but only {n_sw} switches. Independent DECISIONS ≈ {len(spell_ret)} "
          f"spells -> far below 'a few hundred'. Discovery impossible; confirm mode only.")

    # P6 regimes
    for lab, a, b_ in [("2008 crash", "2008-07", "2009-03"), ("2011 bear", "2011-01", "2011-12"),
                       ("2013 taper", "2013-05", "2013-08"), ("2015-16 slide", "2015-03", "2016-02"),
                       ("2017 calm bull", "2017-01", "2017-12")]:
        s = (1 + r.loc[a:b_]).prod() - 1; m = (1 + bh.loc[a:b_]).prod() - 1
        print(f"  P6 {lab:15}: strategy {s:+7.1%}  vs NIFTY {m:+7.1%}")

    # P8 executable: trading AT the signal close vs one day later
    r0, _, _ = run(sig, lag_days=0); c0, _, _ = stats(r0.loc[START:])
    print(f"  P8: trade at signal close (NOT executable, NSE close = 30-min VWAP) CAGR {c0:.2%} vs next day {c:.2%}"
          f" -> lag costs {c0-c:+.2%}/yr")

print("\nC Momentum 30 ETF: P5/P8 FAIL in our window. No ETF traded before 2022; the index history before its "
      "launch is back-calculated (backfill bias). The only honest path is confirm mode via the IIMA WML factor, then a "
      "fresh forward test.")

# %% [markdown]
# ## Read the output like a desk head
# - P2: trend rules trade rarely, so costs are tiny. Their real cost is short-term TAX and whipsaw.
# - P4: if the alpha t is small and beta is around 0.5–0.7, you've mostly built "part-time beta". That's fine for an
#   overlay, but don't call it alpha.
# - P5: under 30 independent decisions in 10 years. That's why we lean on a century of outside evidence (Hurst et al.).
# - P6: look at 2011 and 2015–16 (choppy). That's where trend rules bleed.
# - P8: always trade AFTER the signal is known. Your backtest's close is a 3:00–3:30 pm VWAP, so you can't trade at it.
