# %% [markdown]
# # Day 8 build-along: EDGE FAMILY EXPLORER (look for clues, not strategies)
#
# One quick, PRE-DECLARED test per edge family on Indian index data, so your idea cards start from evidence
# instead of vibes. Rules that make this honest:
# 1. **Exploration sample only: 2007-09 to 2018-12.** 2019-2026 is LOCKED. The loader refuses to return it.
#    The locked years are your future out-of-sample test. Look at them now and they're burned forever.
# 2. **Every test is listed BEFORE running and counted.** N goes in your trial log.
# 3. **The bar is |t| > 3** (Harvey-Liu-Zhu, Day 5). A t of 2 among 8 tests is expected by luck.
# 4. **A pass here is a clue for an idea card, not a strategy.** No costs, no sizing, no out-of-sample yet.
#
# The 8 tests (fixed in advance, one parameter each, no tuning):
# T1 trend: does NIFTY's past-12-month return sign predict next month's return?
# T2 short-term trend: same with past 1 month.
# T3 mean reversion: lag-1 autocorrelation of NIFTY daily returns.
# T4 cross-asset momentum: next-month return of "whichever of NIFTY / gold (GOLDBEES) did better over 6 months" minus the other.
# T5 calendar/event: turn-of-month (last day + first 3 days) vs other days on NIFTY.
# T6 overnight vs intraday: NIFTYBEES close-to-open vs open-to-close mean return.
# T7 pairs: is log(NIFTYBANK/NIFTY) mean-reverting? AR(1) half-life + a crude Dickey-Fuller t.
# T8 volatility regime: does high India VIX (top 20% of past year) predict higher next-month NIFTY return?

# %%
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from pathlib import Path
HERE = Path(__file__).resolve().parent if "__file__" in globals() else Path(".")
DATA = HERE.parent / "09_data"
EXPLORE_END = "2018-12-31"

def load(name):
    d = pd.read_csv(DATA / f"{name}_daily.csv", index_col=0, parse_dates=True).sort_index()
    d = d[~d.index.duplicated()].dropna(subset=["Close"])
    # Bad-tick filter: one-day >8% spike that fully reverses the next day (found on Days 4 and 7)
    lr = np.log(d["Close"]).diff()
    spike = (lr.abs() > 0.08) & (lr.shift(-1).abs() > 0.08) & (np.sign(lr) != np.sign(lr.shift(-1)))
    d = d[~spike]
    return d.loc[:EXPLORE_END]           # <- THE LOCK. Do not edit this line before Day 17.

def nw_t(x, lags=None):
    """Mean and Newey-West t-stat of a series (handles autocorrelation)."""
    x = pd.Series(x).dropna().values; n = len(x); m = x.mean(); e = x - m
    lags = lags if lags is not None else int(4 * (n / 100) ** (2 / 9))
    s = e @ e / n
    for L in range(1, lags + 1):
        s += 2 * (1 - L / (lags + 1)) * (e[L:] @ e[:-L]) / n
    return m, m / np.sqrt(s / n), n

nifty, bank, bees, gold, vix = (load(x) for x in ["NIFTY50", "NIFTYBANK", "NIFTYBEES", "GOLDBEES", "INDIAVIX"])
print(f"Exploration window: {nifty.index[0].date()} to {nifty.index[-1].date()}  ({len(nifty)} NIFTY days). 2019+ is locked.\n")
rows = []

# %% T1/T2 trend (time-series momentum, monthly, non-overlapping)
m = nifty["Close"].resample("ME").last(); mr = np.log(m).diff()
for name, look in [("T1 trend 12m", 12), ("T2 trend 1m", 1)]:
    sig = np.sign(np.log(m).diff(look)).shift(1)          # known at the previous month-end
    strat = (sig * mr).dropna()                            # long if past return > 0, short if < 0 (paper test only: we can't short)
    mu, t, n = nw_t(strat, lags=0)
    rows.append([name, "mean monthly long/short return", f"{mu*100:.2f}%", t, n])

# %% T3 mean reversion (daily autocorrelation)
r = np.log(nifty["Close"]).diff().dropna()
rho = r.autocorr(1); n = len(r)
z = (r - r.mean()) / r.std(); prod = (z * z.shift(1)).dropna()
_, t_rob, _ = nw_t(prod)                                   # robust t (vol clustering makes the naive rho*sqrt(n) too big)
print(f"T3 naive t = {rho*np.sqrt(n):.2f}, robust t = {t_rob:.2f}  <- always use the robust one")
rows.append(["T3 daily autocorrelation", "lag-1 autocorrelation (robust t)", f"{rho:+.3f}", t_rob, n])

# %% T4 cross-asset momentum: NIFTY vs gold
g = gold["Close"].resample("ME").last(); both = pd.concat([m, g], axis=1, keys=["nifty", "gold"]).dropna()
lr6 = np.log(both).diff(6).shift(1); nxt = np.log(both).diff()
winner_minus_loser = np.where(lr6["nifty"] > lr6["gold"], nxt["nifty"] - nxt["gold"], nxt["gold"] - nxt["nifty"])
s4 = pd.Series(winner_minus_loser, index=both.index)[lr6.notna().all(axis=1)]
mu, t, n = nw_t(s4, lags=0)
rows.append(["T4 NIFTY-vs-gold momentum", "mean monthly winner-minus-loser", f"{mu*100:.2f}%", t, n])

# %% T5 turn of month
d = r.to_frame("r"); d["ym"] = d.index.to_period("M")
d["k"] = d.groupby("ym").cumcount(); d["kr"] = d.groupby("ym")["r"].transform("count") - d["k"]   # kr==1: last day
tom = (d["k"] < 3) | (d["kr"] == 1)
diff = d.loc[tom, "r"].mean() - d.loc[~tom, "r"].mean()
se = np.sqrt(d.loc[tom, "r"].var() / tom.sum() + d.loc[~tom, "r"].var() / (~tom).sum())
rows.append(["T5 turn-of-month", "daily mean TOM minus other days", f"{diff*1e4:.1f} bps", diff / se, int(tom.sum())])

# %% T6 overnight vs intraday (NIFTYBEES; index opens on Yahoo are unreliable)
b = bees[(bees["Open"] > 0) & (bees["Close"] > 0)].copy()
on = np.log(b["Open"] / b["Close"].shift()); intra = np.log(b["Close"] / b["Open"])
ok = on.notna() & (on.abs() < 0.10) & (intra.abs() < 0.10)       # drop broken opens (zeros / glitches)
print(f"T6: dropped {(~ok).sum()} NIFTYBEES days with missing or broken opens")
on, intra = on[ok], intra[ok]
mu, t, n = nw_t(on - intra, lags=5)
rows.append(["T6 overnight minus intraday", "daily mean (NIFTYBEES)", f"{mu*1e4:.1f} bps", t, n])

# %% T7 pairs: NIFTYBANK / NIFTY
spread = np.log(bank["Close"] / nifty["Close"]).dropna()
ds = spread.diff().dropna(); lag = spread.shift(1).loc[ds.index]
X = np.column_stack([np.ones(len(lag)), lag.values]); beta = np.linalg.lstsq(X, ds.values, rcond=None)[0]
res = ds.values - X @ beta; se_b = np.sqrt(res @ res / (len(res) - 2) / ((lag - lag.mean()) ** 2).sum())
df_t = beta[1] / se_b; half_life = -np.log(2) / beta[1] if beta[1] < 0 else np.inf
rows.append(["T7 BANK/NIFTY spread", f"Dickey-Fuller t (5% crit about -2.86); half-life {half_life:.0f} days", f"{beta[1]:+.5f}", df_t, len(ds)])

# %% T8 VIX regime
v = vix["Close"].resample("ME").last()
hi = (v > v.rolling(12).quantile(0.8)).shift(1)
dd = pd.concat([mr, hi], axis=1, keys=["r", "hi"]).dropna(); dd["hi"] = dd["hi"].astype(bool)
diff = dd.loc[dd.hi, "r"].mean() - dd.loc[~dd.hi, "r"].mean()
se = np.sqrt(dd.loc[dd.hi, "r"].var() / dd.hi.sum() + dd.loc[~dd.hi, "r"].var() / (~dd.hi).sum())
rows.append(["T8 high-VIX months", "next-month NIFTY: high-VIX minus normal", f"{diff*100:.2f}%", diff / se, int(dd.hi.sum())])

# %% Report
tab = pd.DataFrame(rows, columns=["test", "statistic", "value", "t", "n"])
tab["passes |t|>3?"] = np.where(tab["test"].str.startswith("T7"), "n/a (see DF note)", np.where(tab["t"].abs() > 3, "YES", "no"))
pd.set_option("display.width", 200, "display.max_colwidth", 60)
print(tab.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
k = len(tab)
print(f"\nTrials this lab: {k}. Add {k} to your trial log. With {k} tests, the chance that at least one |t|>2 appears by pure luck is about {1-(0.954**k):.0%}.")

fig, ax = plt.subplots(1, 3, figsize=(16, 4.5))
ax[0].plot((1 + (np.sign(np.log(m).diff(12)).shift(1) * mr).fillna(0)).cumprod(), label="T1 12m trend (long/short, paper)")
ax[0].plot((1 + mr.fillna(0)).cumprod(), label="NIFTY buy & hold"); ax[0].set_yscale("log"); ax[0].legend(fontsize=8); ax[0].set_title("T1: trend vs holding (2007-2018)")
ax[1].plot(spread); ax[1].set_title(f"T7: log(BANK/NIFTY), half-life {half_life:.0f}d"); 
ax[2].bar(range(k), tab["t"].abs()); ax[2].axhline(3, color="r", ls="--", label="t = 3 bar"); ax[2].axhline(2, color="gray", ls=":", label="t = 2 (not enough)")
ax[2].set_xticks(range(k)); ax[2].set_xticklabels([x.split()[0] for x in tab["test"]]); ax[2].legend(); ax[2].set_title("|t| by test")
plt.tight_layout(); plt.savefig(HERE / "edge_family_explorer.png", dpi=105); print("Saved edge_family_explorer.png")

# %% [markdown]
# ## Questions for your log
# 1. Which tests clear |t| > 3? Which only clear 2? Given 8 tests, how many |t| > 2 would you expect from luck alone?
# 2. T1 and T2 are "long/short" paper tests. You can't short NIFTY in our program (no F&O, no borrowing). What
#    long/flat version would you put on an idea card, and why might it be weaker?
# 3. T3: the index shows POSITIVE daily autocorrelation (continuation, not reversal). Part of it is an index artefact:
#    stale prices of less-liquid constituents (Lo-MacKinlay 1990). Is it tradeable in NIFTYBEES after Day 7's costs?
#    Why did the robust t come out smaller than the naive t?
# 4. T7: the spread trends for years. Why is "two related indices" not the same as "a mean-reverting pair"?
# 5. T6: why use NIFTYBEES and not the NIFTY index for overnight vs intraday? (Hint: check how often the index
#    'Open' equals the previous close in this data.)
# 6. Pick ONE family whose result surprised you and write a 3-line "why would this pay?" before any idea card.
