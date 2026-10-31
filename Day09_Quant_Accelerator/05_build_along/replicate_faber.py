# %% [markdown]
# # Day 9 build-along: REPLICATE A PAPER (Faber's 10-month moving-average rule) on Indian data
# Diwali light day: one small, careful replication. The skill matters more than the result.
#
# Paper rule (Faber 2006/2013): at each month-end, if price > its 10-month simple moving average, hold the asset
# next month; otherwise hold cash. ONE parameter (10 months), taken from the paper, NOT tuned.
#
# Our version:
# - NIFTY 50 (price index: no dividends, so buy-and-hold is understated by about 1-1.5% a year. Note it, don't fix it.)
# - Plus a 2-asset version: 50% NIFTY, 50% gold (GOLDBEES), each with its own 10-month filter (Faber's multi-asset spirit)
# - Cash earns an ASSUMED 6% a year (a rough Indian short-rate proxy. It's an assumption: say so in your notes)
# - Exploration window only: the series ends 2018-12-31. 2019+ stays locked.
# - Day 7 costs on every switch (delivery, equity ETF, at Rs 1 lakh) + 5 bps assumed spread per side.
# Counts as 2 trials. Log them.

# %%
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from pathlib import Path
from nse_costs import round_trip
HERE = Path(__file__).resolve().parent if "__file__" in globals() else Path(".")
END = "2018-12-31"; CASH = 0.06; SPREAD_BPS = 5; CAPITAL = 1e5

def monthly(name):
    d = pd.read_csv(HERE.parent / "08_data" / f"{name}_daily.csv", index_col=0, parse_dates=True)["Close"].dropna().sort_index()
    lr = np.log(d).diff()
    spike = (lr.abs() > 0.08) & (lr.shift(-1).abs() > 0.08) & (np.sign(lr) != np.sign(lr.shift(-1)))
    return d[~spike].loc[:END].resample("ME").last()

cost_frac = (round_trip(CAPITAL, CAPITAL, "delivery", "etf_equity")["total"] / CAPITAL) / 2 + SPREAD_BPS / 1e4   # per one-way switch

def faber(px, sma=10):
    r = px.pct_change()
    inside = (px > px.rolling(sma).mean()).astype(float).shift(1)      # decided at last month-end, held this month
    inside = inside.where(px.rolling(sma).mean().shift(1).notna())
    strat = inside * r + (1 - inside) * CASH / 12
    switches = inside.diff().abs().fillna(0)
    strat_net = strat - switches * cost_frac
    ok = inside.notna()
    return r[ok], strat[ok], strat_net[ok], switches[ok]

def stats(x, label):
    eq = (1 + x).cumprod(); yrs = len(x) / 12
    cagr = eq.iloc[-1] ** (1 / yrs) - 1; vol = x.std() * np.sqrt(12)
    sharpe = (x.mean() * 12 - CASH) / vol
    dd = (eq / eq.cummax() - 1).min()
    return {"": label, "CAGR": f"{cagr:6.2%}", "vol": f"{vol:6.2%}", "Sharpe(vs 6% cash)": f"{sharpe:5.2f}", "max DD": f"{dd:7.2%}", "months": len(x)}

nifty, gold = monthly("NIFTY50"), monthly("GOLDBEES")
bh, s, sn, sw = faber(nifty)
gbh, gs, gsn, gsw = faber(gold)
idx = sn.index.intersection(gsn.index)
mix_bh = 0.5 * bh.loc[idx] + 0.5 * gbh.loc[idx]
mix = 0.5 * sn.loc[idx] + 0.5 * gsn.loc[idx]

rows = [stats(bh, "NIFTY buy & hold"), stats(s, "NIFTY 10m filter, gross"), stats(sn, "NIFTY 10m filter, net"),
        stats(mix_bh.dropna(), "50/50 NIFTY+gold, hold (monthly rebal, no cost)"), stats(mix.dropna(), "50/50, each 10m filter, net")]
print(f"Window: {bh.index[0]:%Y-%m} to {bh.index[-1]:%Y-%m}. Cost per switch = {cost_frac*1e4:.1f} bps. NIFTY switches: {int(sw.sum())}, gold switches: {int(gsw.sum())}\n")
print(pd.DataFrame(rows).to_string(index=False))
print("\nTrials: +2 (NIFTY filter, 50/50 filter). Paper's claim to check: 'similar return, lower volatility and drawdown.'")

fig, ax = plt.subplots(1, 2, figsize=(14, 4.5))
for x, l in [(bh, "NIFTY hold"), (sn, "NIFTY 10m filter (net)")]:
    ax[0].plot((1 + x).cumprod(), label=l)
ax[0].set_yscale("log"); ax[0].legend(); ax[0].set_title("Faber rule on NIFTY, 2008-2018 (exploration only)")
for x, l in [(bh, "NIFTY hold"), (sn, "NIFTY 10m filter (net)"), (mix.dropna(), "50/50 filtered (net)")]:
    eq = (1 + x).cumprod(); ax[1].plot(eq / eq.cummax() - 1, label=l)
ax[1].legend(); ax[1].set_title("Drawdowns")
plt.tight_layout(); plt.savefig(HERE / "replicate_faber.png", dpi=105); print("Saved replicate_faber.png")

# %% [markdown]
# ## Questions for your log
# 1. Did the paper's main claim (similar return, lower volatility and drawdown) hold on NIFTY 2008-2018? Which part did and which didn't?
# 2. How many switches, and what did costs take? Why is cost NOT the problem for this rule (Day 7)? What IS the main hidden cost? (Hint: tax on each exit.)
# 3. The window starts in 2008, right after a crash. How does that start date flatter the filter? What would you need to be fair?
# 4. Our cash rate is an assumption. Rerun with CASH = 0.04 and 0.07 (log as trials!). How sensitive is the conclusion?
# 5. Faber says it's a risk-reduction tool, not a return enhancer. Does that make it a good idea card for us? Score it with the template.
# 6. Marmi et al. (2009) criticised the paper with bootstrap tests. In one paragraph: what would a bootstrap test of THIS result look like?
