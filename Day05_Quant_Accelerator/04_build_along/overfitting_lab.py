# %% [markdown]
# # Day 5 build-along: THE OVERFITTING LAB
# Deliverable: proof that the best noise strategy is fake.
#
# 1. Make 20 strategies that are pure coin flips, run on REAL NIFTY returns. Crown the best one.
# 2. Out-of-sample: watch the champion fall apart.
# 3. Repeat the contest 2,000 times: the "best of N" is always impressive. Compare with the False Strategy Theorem.
# 4. More trials -> higher fake Sharpe: the sqrt(2 ln N) curve.
# 5. Deflated Sharpe Ratio (Bailey & Lopez de Prado 2014) on the champion.
# 6. Probability of Backtest Overfitting via CSCV (Bailey et al. 2017).
# 7. Minimum Backtest Length table.
# 8. Control: plant ONE real edge and see if the tools can find it.
# RULE: fill prediction-sheet.md before running.

# %%
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from itertools import combinations
from pathlib import Path
from scipy.stats import norm, skew, kurtosis

rng = np.random.default_rng(7)
DATA = (Path(__file__).resolve().parent.parent / "03_data") if "__file__" in globals() else Path("../03_data")
px = pd.read_csv(DATA / "NIFTY50_daily.csv", index_col=0, parse_dates=True)["Close"].dropna()
r = np.log(px).diff().dropna().values           # real NIFTY daily log returns, 2007-2026
T = len(r); split = int(T * 0.7)
GAMMA = 0.5772156649                            # Euler-Mascheroni
ann = np.sqrt(252)

def sharpe(x, axis=0):
    return x.mean(axis=axis) / x.std(axis=axis, ddof=1) * ann

def noise_strategies(n, hold=5):
    """n random long/short strategies: a coin decides +1/-1, held for `hold` days, applied to tomorrow's return.
    They look like 'real' strategies (they trade, they have drawdowns) but have zero skill by construction."""
    blocks = int(np.ceil(T / hold))
    sig = rng.choice([-1.0, 1.0], size=(blocks, n)).repeat(hold, axis=0)[:T]
    return sig * r[:, None]

def expected_max_z(N):
    """False Strategy Theorem: expected maximum of N independent standard normals (approx)."""
    if N == 1: return 0.0
    return (1 - GAMMA) * norm.ppf(1 - 1 / N) + GAMMA * norm.ppf(1 - 1 / (N * np.e))

fig, ax = plt.subplots(2, 3, figsize=(17, 10))

# %% [markdown]
# ## 1-2. Twenty coin-flip strategies, first 70% in-sample, last 30% out-of-sample

# %%
print(f"NIFTY data: {T} daily returns. In-sample {split} days (~{split/252:.1f} yrs), out-of-sample {T-split} days (~{(T-split)/252:.1f} yrs)")
S = noise_strategies(20)
is_sr, oos_sr = sharpe(S[:split]), sharpe(S[split:])
best = int(np.argmax(is_sr))
print("\n=== 1. THE CONTEST (in-sample) ===")
order = np.argsort(-is_sr)
for k in order[:5]:
    print(f"  strategy #{k:2d}: IS Sharpe {is_sr[k]:+.2f}")
print(f"  ... worst: {is_sr.min():+.2f}.  Champion = #{best}, IS Sharpe {is_sr[best]:+.2f}")
print("\n=== 2. OUT-OF-SAMPLE ===")
print(f"  Champion OOS Sharpe {oos_sr[best]:+.2f}   (average OOS of all 20: {oos_sr.mean():+.2f})")
print(f"  Corr(IS Sharpe, OOS Sharpe) across the 20 = {np.corrcoef(is_sr, oos_sr)[0,1]:+.2f}  (skill would make this clearly positive)")
eq = np.exp(np.cumsum(S, axis=0))
for k in range(20):
    ax[0, 0].plot(eq[:, k], color="red" if k == best else "grey", lw=1.6 if k == best else 0.5, alpha=1 if k == best else 0.6)
ax[0, 0].axvline(split, color="k", ls="--"); ax[0, 0].set_yscale("log")
ax[0, 0].set_title(f"1-2. 20 coin-flip strategies on real NIFTY\nred = IS champion (IS SR {is_sr[best]:.2f}, OOS SR {oos_sr[best]:.2f}); dashed = OOS starts")

# %% [markdown]
# ## 3. Run the contest 2,000 times

# %%
print("\n=== 3. 2,000 CONTESTS OF 20 ===")
M, N = 2000, 20
best_is, best_oos = np.empty(M), np.empty(M)
for m in range(M):
    s = noise_strategies(N); a, b = sharpe(s[:split]), sharpe(s[split:])
    i = np.argmax(a); best_is[m], best_oos[m] = a[i], b[i]
y_is = split / 252
theory = expected_max_z(N) / np.sqrt(y_is)        # annualised SR of a zero-skill strategy ~ N(0, 1/years)
print(f"  Average champion IS Sharpe:  {best_is.mean():.2f}   False Strategy Theorem predicts ~{theory:.2f}")
print(f"  Champion IS Sharpe > 0.5 in {np.mean(best_is>0.5):.0%} of contests;  > 1.0 in {np.mean(best_is>1.0):.1%}")
print(f"  Average champion OOS Sharpe: {best_oos.mean():+.2f}   (zero, as it must be)")
ax[0, 1].hist(best_is, bins=50, alpha=0.7, label="champion IS SR"); ax[0, 1].hist(best_oos, bins=50, alpha=0.7, label="same champion OOS SR")
ax[0, 1].axvline(theory, color="k", ls="--", label=f"theory E[max] = {theory:.2f}")
ax[0, 1].legend(); ax[0, 1].set_title("3. 2,000 contests: the winner always looks good IS,\nand is exactly average OOS")

# %% [markdown]
# ## 4. More trials, higher fake Sharpe

# %%
print("\n=== 4. HOW MANY TRIES DOES IT TAKE? (full 19-yr sample) ===")
Ns = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
years = T / 252
pool = noise_strategies(1000); pool_sr = sharpe(pool)
emp = [np.max(pool_sr[:n]) for n in Ns]
th = [expected_max_z(n) / np.sqrt(years) for n in Ns]
for n, e, t in zip(Ns, emp, th):
    print(f"  N={n:5d}: best Sharpe found {e:+.2f}   theory E[max] {t:.2f}")
ax[0, 2].plot(Ns, emp, "o-", label="best of N (one run)"); ax[0, 2].plot(Ns, th, "k--", label="False Strategy Theorem")
ax[0, 2].set_xscale("log"); ax[0, 2].legend(); ax[0, 2].set_xlabel("number of strategies tried (N)")
ax[0, 2].set_title(f"4. Zero-skill Sharpe you can 'find' on {years:.0f} yrs of data\ngrows like sqrt(2 ln N)")

# %% [markdown]
# ## 5. Deflated Sharpe Ratio on the champion of 1,000
# PSR(SR*) = Phi( (SR - SR*) sqrt(T-1) / sqrt(1 - skew*SR + (kurt-1)/4 * SR^2) ), all Sharpe ratios PER PERIOD (daily).
# DSR = PSR with SR* = the Sharpe you'd expect from the best of N zero-skill trials.

# %%
def psr(x, sr_star):
    x = np.asarray(x); sr = x.mean() / x.std(ddof=1)
    g3, g4 = skew(x), kurtosis(x, fisher=False)
    return norm.cdf((sr - sr_star) * np.sqrt(len(x) - 1) / np.sqrt(1 - g3 * sr + (g4 - 1) / 4 * sr**2))

def dsr(returns_matrix, k):
    daily_sr = returns_matrix.mean(0) / returns_matrix.std(0, ddof=1)
    sr_star = np.std(daily_sr, ddof=1) * expected_max_z(returns_matrix.shape[1])
    return psr(returns_matrix[:, k], sr_star), sr_star

k = int(np.argmax(pool_sr))
naive = psr(pool[:, k], 0.0); d, sr_star = dsr(pool, k)
print("\n=== 5. DEFLATED SHARPE (champion of 1,000 on full data) ===")
print(f"  Champion annual Sharpe {pool_sr[k]:.2f}")
print(f"  Naive PSR (prob. true SR > 0, ignoring the 999 others): {naive:.3f}  <- looks 'significant'")
print(f"  Benchmark SR* from 1,000 trials: {sr_star*ann:.2f} annual")
print(f"  DEFLATED Sharpe Ratio: {d:.3f}   (need > 0.95 to believe it) -> {'PASS' if d>0.95 else 'FAIL: it is luck'}")

# %% [markdown]
# ## 6. Probability of Backtest Overfitting (CSCV), on the 20 strategies
# Cut time into 16 blocks. For every way to pick 8 as in-sample (12,870 ways): crown the IS best, see where it ranks
# in the other 8. PBO = share of splits where the IS winner lands in the bottom half OOS.

# %%
def pbo_cscv(R, S=16):
    Tn = (len(R) // S) * S; blocks = np.array_split(R[:Tn], S)
    logits = []
    for c in combinations(range(S), S // 2):
        IS = np.vstack([blocks[i] for i in c]); OOS = np.vstack([blocks[i] for i in range(S) if i not in c])
        n_star = np.argmax(sharpe(IS))
        rank = (sharpe(OOS).argsort().argsort()[n_star] + 1) / (R.shape[1] + 1)   # relative OOS rank in (0,1)
        logits.append(np.log(rank / (1 - rank)))
    logits = np.array(logits)
    return np.mean(logits <= 0), logits

pbo, lg = pbo_cscv(S)
print("\n=== 6. PBO (CSCV, S=16, 12,870 splits) on the 20 noise strategies ===")
print(f"  PBO = {pbo:.2f}   (~0.5 means picking the IS winner is no better than a coin; real skill pushes it toward 0)")
ax[1, 0].hist(lg, bins=40, color="grey"); ax[1, 0].axvline(0, color="r")
ax[1, 0].set_title(f"6. CSCV logits of the IS winner's OOS rank\nnoise: PBO = {pbo:.2f} (mass left of red line)")

# %% [markdown]
# ## 7. Minimum Backtest Length
# If you try N zero-skill ideas, how many years of data until the best one is EXPECTED to show a Sharpe below 1?
# MinBTL ~ (E[max of N] / target SR)^2  years  (Bailey, Borwein, Lopez de Prado, Zhu 2014)

# %%
print("\n=== 7. MINIMUM BACKTEST LENGTH (expected best fake Sharpe < 1.0) ===")
rows = []
for n in [1, 5, 10, 20, 45, 100, 1000]:
    mb = (expected_max_z(n) / 1.0) ** 2
    rows.append((n, mb)); print(f"  N={n:5d} trials -> need > {mb:4.1f} years of data")
ax[1, 1].plot([a for a, _ in rows], [b for _, b in rows], "o-"); ax[1, 1].set_xscale("log")
ax[1, 1].axhline(years, color="r", ls="--", label=f"your NIFTY data: {years:.0f} yrs"); ax[1, 1].legend()
ax[1, 1].set_xlabel("N trials"); ax[1, 1].set_ylabel("years"); ax[1, 1].set_title("7. MinBTL for target Sharpe 1.0")

# %% [markdown]
# ## 8. Control: plant one REAL edge among 19 noise strategies
# A strategy with a true annual Sharpe of about 1.0 (noise + small genuine drift). Can the tools see it?

# %%
print("\n=== 8. CONTROL: ONE REAL EDGE (true annual SR ~1.0) ===")
S2 = noise_strategies(20)
true_sr = 1.0; vol = S2[:, 0].std()
S2[:, 0] = S2[:, 0] + true_sr / ann * vol            # add drift worth SR ~1.0
sr2 = sharpe(S2); k2 = int(np.argmax(sr2))
d2, _ = dsr(S2, k2); pbo2, lg2 = pbo_cscv(S2)
print(f"  Best strategy = #{k2} ({'the real one' if k2==0 else 'a noise one!'}), annual Sharpe {sr2[k2]:.2f}")
print(f"  DSR {d2:.3f} ({'PASS' if d2>0.95 else 'FAIL'}),  PBO {pbo2:.2f}")
print("  Read this honestly: PBO points at the real edge, but DSR may still say FAIL. Luck in the realised Sharpe\n"
      "  plus the selection penalty make the bar tough on purpose. Real edges of SR ~1 are hard to PROVE even with\n"
      "  19 years. With 2 years they are nearly impossible to prove: try it (question 5).")
ax[1, 2].hist(lg2, bins=40, color="green"); ax[1, 2].axvline(0, color="r")
ax[1, 2].set_title(f"8. Same test with one real edge planted\nPBO = {pbo2:.2f}")

plt.tight_layout(); plt.savefig("overfitting_lab.png", dpi=105); print("\nSaved overfitting_lab.png")

# %% [markdown]
# ## Questions for your log
# 1. Your champion's IS Sharpe vs OOS Sharpe. In one sentence, why did it collapse?
# 2. From part 4: if you test 100 SMA variants on 19 years of NIFTY, what Sharpe should you EXPECT from pure luck?
# 3. Why does DSR need the variance of Sharpe ratios ACROSS your trials, not just their count?
# 4. Our plan says Day 12 locks a FIXED small parameter grid and a t > 3 bar. Using part 7, justify both rules with numbers.
# 5. Part 8 used 19 years. Re-run with only the last 2 years of data. Does the real edge still pass? What does that say about "I tested it on 2023-2025"?
