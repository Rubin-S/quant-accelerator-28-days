import warnings; warnings.filterwarnings('ignore')
# %% [markdown]
# # Day 4 build-along: NIFTY STATS LAB (real data, 2007-2026)
# Your Day 4 deliverable: a stats notebook on 10+ years of NIFTY.
#
# 0. Data audit FIRST: this data has a real trap in it. Find it before you trust anything.
# 1. Simple vs log returns
# 2. Volatility: annualise it, watch it cluster, measure it by year
# 3. Fat tails: how often does a "4-sigma" day really happen?
# 4. Correlation: Bank Nifty, S&P 500 (time-zone trap!), gold, and what happens to correlation in a crash
# 5. Price index vs what you'd actually earn (dividends)
#
# Data: Yahoo Finance via yfinance, downloaded 31 Oct 2026, in ../03_data/. Free data. Treat it as untrusted.
# RULE: fill prediction-sheet.md before each part.

# %%
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from math import erf, sqrt
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "03_data" if "__file__" in globals() else Path("../03_data")
def load(name):
    d = pd.read_csv(DATA / f"{name}_daily.csv", index_col=0, parse_dates=True)
    return d["Close"]

px = {n: load(n) for n in ["NIFTY50", "NIFTYBANK", "NIFTYBEES", "GOLDBEES", "SP500", "INDIAVIX"]}

# %% [markdown]
# ## 0. Data audit (always first)
# Check: missing values, duplicate dates, and one-day moves too big to be real.

# %%
print("=== 0. DATA AUDIT ===")
for n, s in px.items():
    r = np.log(s).diff()
    print(f"{n:10s} rows {len(s):5d}  {s.index.min().date()} -> {s.index.max().date()}  "
          f"NaN {s.isna().sum()}  dup dates {s.index.duplicated().sum()}  biggest |log move| {r.abs().max():.2f} on {r.abs().idxmax().date()}")
print("\nNIFTYBEES around Dec 2019:")
print(px["NIFTYBEES"].loc["2019-12-17":"2019-12-24"].round(2).to_string())
print("-> On 19-20 Dec 2019 the price shows ~13 instead of ~129 (GOLDBEES: ~0.34 instead of ~34).\n"
      "   Most likely a unit-split adjustment the data vendor applied wrongly on those dates (check the AMC's notice). A 'return' of -90% then +900% is a DATA ERROR, not a crash.\n"
      "   If your backtest had traded those two days, it would show a fake fortune or a fake ruin.")

def clean(s, max_move=0.25):
    """Drop NaNs and isolated bad ticks: a day whose move in AND move out are both > max_move in opposite directions."""
    s = s.dropna()
    for _ in range(3):
        r = np.log(s).diff()
        bad = (r.abs() > max_move) & (r.shift(-1).abs() > max_move) & (np.sign(r) != np.sign(r.shift(-1)))
        # a 2-day bad patch: flag both days
        bad2 = (r.abs() > max_move) & (r.shift(-2).abs() > max_move) & (np.sign(r) != np.sign(r.shift(-2)))
        idx = s.index[bad] .union(s.index[bad2]).union(s.index[bad2.shift(1, fill_value=False)])
        if len(idx) == 0: break
        print(f"   removing {len(idx)} bad rows from {s.name or ''}: {[d.date().isoformat() for d in idx]}")
        s = s.drop(idx)
    return s

for n in ["NIFTYBEES", "GOLDBEES"]:          # only the ETFs: VIX can legitimately jump 25%+ and back
    px[n] = clean(px[n].rename(n))
for n in px: px[n] = px[n].dropna()
print("After cleaning, biggest NIFTYBEES |log move|:", round(np.log(px['NIFTYBEES']).diff().abs().max(), 3))

nifty = px["NIFTY50"]
r = np.log(nifty).diff().dropna()          # daily LOG returns
R = nifty.pct_change().dropna()            # daily SIMPLE returns
fig, ax = plt.subplots(3, 2, figsize=(14, 13))

# %% [markdown]
# ## 1. Simple vs log returns
# Simple: R = P1/P0 - 1  (adds across ASSETS in a portfolio)
# Log:    r = ln(P1/P0)  (adds across TIME)
# +10% then -10% is NOT break-even. Log returns make that obvious.

# %%
print("\n=== 1. SIMPLE vs LOG ===")
yrs = (nifty.index[-1] - nifty.index[0]).days / 365.25
print(f"NIFTY {nifty.index[0].date()} {nifty.iloc[0]:.0f} -> {nifty.index[-1].date()} {nifty.iloc[-1]:.0f} over {yrs:.1f} years")
print(f"  sum of daily log returns  = {r.sum():.4f}   ln(end/start) = {np.log(nifty.iloc[-1]/nifty.iloc[0]):.4f}   (identical: logs add)")
print(f"  sum of daily simple rets  = {R.sum():.4f}   actual total  = {nifty.iloc[-1]/nifty.iloc[0]-1:.4f}   (NOT equal: simple returns don't add over time)")
print(f"  arithmetic mean daily x252 = {R.mean()*252:.2%}  vs  CAGR = {(nifty.iloc[-1]/nifty.iloc[0])**(1/yrs)-1:.2%}")
print(f"  The gap is volatility drag, about sigma^2/2 = {(R.std()*np.sqrt(252))**2/2:.2%}/yr. Same idea as Day 3's Kelly curve.")
print("  (Price index only: NIFTY 50 'Close' here excludes dividends. See Part 5.)")

# %% [markdown]
# ## 2. Volatility
# Annualised vol = daily std x sqrt(252). Volatility is NOT constant: it clusters.

# %%
print("\n=== 2. VOLATILITY ===")
dvol = r.std(); print(f"Daily vol {dvol:.3%}  ->  annualised {dvol*np.sqrt(252):.1%}")
by_year = r.groupby(r.index.year).std() * np.sqrt(252)
print("Annualised vol by year:"); print((by_year*100).round(1).to_string())
roll = r.rolling(21).std() * np.sqrt(252)
ax[0, 0].plot(roll.index, roll*100, lw=0.8)
ax[0, 0].set_title(f"2. NIFTY 21-day rolling vol (annualised %)\nLong-run average {dvol*np.sqrt(252):.0%}, but it lives in regimes")
ax[0, 0].set_ylabel("%")
def acf(x, lags):
    x = x - x.mean(); v = (x*x).sum()
    return np.array([(x[:-k]*x[k:]).sum()/v for k in lags])
lags = np.arange(1, 61); xs = r.values
a_r, a_abs = acf(xs, lags), acf(np.abs(xs), lags)
ax[0, 1].bar(lags-0.2, a_r, width=0.4, label="returns")
ax[0, 1].bar(lags+0.2, a_abs, width=0.4, label="|returns|")
ax[0, 1].axhline(2/np.sqrt(len(xs)), color="k", ls="--", lw=0.8); ax[0, 1].axhline(-2/np.sqrt(len(xs)), color="k", ls="--", lw=0.8)
ax[0, 1].set_title("2. Autocorrelation: returns ~ none, |returns| = strong & slow\nDirection is hard to predict. Size (vol) is not."); ax[0, 1].legend(); ax[0, 1].set_xlabel("lag (days)")
print(f"Autocorr lag 1: returns {a_r[0]:+.3f}, |returns| {a_abs[0]:+.3f}.  Lag 20: returns {a_r[19]:+.3f}, |returns| {a_abs[19]:+.3f}")
fwd = r.abs().rolling(21).mean().shift(-21)
ok = fwd.notna()
print(f"Leverage effect: corr(today's return, next-21-day avg |return|) = {np.corrcoef(r[ok], fwd[ok])[0,1]:+.3f}  (negative: falls raise future vol)")

# %% [markdown]
# ## 3. Fat tails
# If returns were normal, a 4-sigma day would happen about once every 60 years (twice-sided ~ 0.0063%).

# %%
print("\n=== 3. FAT TAILS ===")
z = (r - r.mean()) / r.std()
norm_tail = lambda k: 1 - erf(k/sqrt(2))           # P(|Z| > k) for a normal
n = len(z)
print(f"{len(z)} days. Skew {r.skew():+.2f}, excess kurtosis {r.kurt():.1f} (normal = 0)")
print(f"{'beyond':>8} | {'actual days':>11} | {'normal predicts':>15} | {'normal: once every':>20}")
for k in [2, 3, 4, 5, 6]:
    act = int((z.abs() > k).sum()); exp = n * norm_tail(k)
    print(f"{k:>7}σ | {act:>11d} | {exp:>15.4g} | {1/(norm_tail(k)*252):>14,.1f} years")
print("Worst 5 days:"); print((r.nsmallest(5)*100).round(2).to_string())
print("Best 5 days:");  print((r.nlargest(5)*100).round(2).to_string())
try:
    from scipy import stats
    (osm, osr), _ = stats.probplot(z.values, dist="norm")
    ax[1, 0].scatter(osm, osr, s=3); ax[1, 0].plot([-5, 5], [-5, 5], "r--")
    ax[1, 0].set_title("3. Q-Q plot vs normal: the ends bend away = fat tails"); ax[1, 0].set_xlabel("normal quantile"); ax[1, 0].set_ylabel("NIFTY z-score")
except ImportError:
    ax[1, 0].text(0.1, 0.5, "pip install scipy for the Q-Q plot")
bins = np.linspace(-8, 8, 161)
ax[1, 1].hist(z, bins=bins, density=True, alpha=0.6, label="NIFTY daily z")
xx = np.linspace(-8, 8, 400); ax[1, 1].plot(xx, np.exp(-xx**2/2)/np.sqrt(2*np.pi), "r", label="normal")
ax[1, 1].set_yscale("log"); ax[1, 1].set_ylim(1e-5, 1); ax[1, 1].legend()
ax[1, 1].set_title("3. Same thing on a log scale: the tails are where you get hurt")

# %% [markdown]
# ## 4. Correlation
# Trap: the S&P 500 closes AFTER the NSE (it's night in India). Today's US move shows up in TOMORROW's NIFTY.

# %%
print("\n=== 4. CORRELATION (daily log returns, overlapping dates) ===")
rets = pd.DataFrame({k: np.log(v).diff() for k, v in px.items() if k != "INDIAVIX"}).dropna()
print(rets.corr().round(2).to_string())
both = pd.concat([np.log(px["NIFTY50"]).diff().rename("nifty"), np.log(px["SP500"]).diff().rename("spx")], axis=1).dropna()
same = both.corr().iloc[0, 1]
lagged = both["nifty"].corr(both["spx"].shift(1))
print(f"NIFTY vs S&P same date: {same:+.2f}   NIFTY today vs S&P YESTERDAY: {lagged:+.2f}")
print("  TRAP: the S&P's session on date t happens AFTER the NSE closes on date t (IST night).\n"
      "  So the same-date number uses information you could never have had while NIFTY was trading.\n"
      "  Only the lagged number is tradeable. Mixing time zones on one date index is a classic look-ahead bug.")
vix = px["INDIAVIX"]; dv = np.log(vix).diff()
j = pd.concat([np.log(px["NIFTY50"]).diff().rename("n"), dv.rename("v")], axis=1).dropna()
print(f"NIFTY return vs India VIX change: {j.corr().iloc[0,1]:+.2f}")
rc = rets["NIFTY50"].rolling(126).corr(rets["GOLDBEES"])
rb = rets["NIFTY50"].rolling(126).corr(rets["NIFTYBANK"])
ax[2, 0].plot(rc.index, rc, label="NIFTY vs Gold ETF"); ax[2, 0].plot(rb.index, rb, label="NIFTY vs Bank Nifty")
ax[2, 0].axhline(0, color="k", lw=0.8); ax[2, 0].legend(); ax[2, 0].set_title("4. Rolling 6-month correlation: it moves a lot")
calm = rets["NIFTY50"].abs() < rets["NIFTY50"].abs().quantile(0.8)
for k in ["NIFTYBANK", "GOLDBEES"]:
    print(f"corr NIFTY~{k}: calm days {rets.loc[calm,'NIFTY50'].corr(rets.loc[calm,k]):+.2f} | big-move days (top 20% |NIFTY|) {rets.loc[~calm,'NIFTY50'].corr(rets.loc[~calm,k]):+.2f}")
print("(Careful: conditioning on big moves raises measured correlation by itself. Day 5 will teach you to distrust this kind of slice.)")

# %% [markdown]
# ## 5. Price index vs what you'd earn
# NIFTY 50 'Close' is a PRICE index: no dividends. NIFTYBEES is an ETF you can buy: it holds the stocks and
# (as an accumulating-style fund in recent years) reflects dividends, minus fees. Compare them.

# %%
print("\n=== 5. PRICE INDEX vs ETF ===")
pair = pd.concat([px["NIFTY50"], px["NIFTYBEES"]], axis=1).dropna()
pair = pair.loc["2010-01-01":]
g = pair.iloc[-1] / pair.iloc[0]; y = (pair.index[-1]-pair.index[0]).days/365.25
print(f"From {pair.index[0].date()} to {pair.index[-1].date()} ({y:.1f} yrs): NIFTY price CAGR {g.iloc[0]**(1/y)-1:.2%}, NIFTYBEES CAGR {g.iloc[1]**(1/y)-1:.2%}")
print("Any gap = dividends, fund fees, tracking error and fund distributions. Find out which (see RESOURCES: NSE TRI).")
norm = pair / pair.iloc[0]
ax[2, 1].plot(norm.index, norm.iloc[:, 0], label="NIFTY 50 price index"); ax[2, 1].plot(norm.index, norm.iloc[:, 1], label="NIFTYBEES ETF")
ax[2, 1].set_yscale("log"); ax[2, 1].legend(); ax[2, 1].set_title("5. Growth of 1 since 2010 (log scale)")

plt.tight_layout(); plt.savefig("nifty_stats_lab.png", dpi=110); print("\nSaved nifty_stats_lab.png")

# %% [markdown]
# ## Questions for your log
# 1. What was the data trap in Part 0, and what would it have done to a backtest? Write a one-line audit rule that catches it.
# 2. NIFTY's full-sample vol is about 20%, but most calm years sit at 10-16%. Which years were double the calm level? What did Day 3's Kelly maths assume about vol?
# 3. Fat tails: how many times more often than "normal" do 4-sigma days happen? What does that do to a risk limit set as "3 sigma"?
# 4. Why is NIFTY-today vs S&P-yesterday higher than same-day? Name one way this trap could fake an "edge" in a backtest.
# 5. Returns barely autocorrelate, |returns| do strongly. What does that tell you about what is forecastable: direction or risk?
