# %% [markdown]
# # Day 3 build-along: KELLY LAB
# How much should you bet when you have an edge?
#
# 1. The growth curve: why betting MORE can make you grow SLOWER
# 2. Full vs half vs 2x Kelly to ruin: 10,000 players replay the Haghani-Dewey biased-coin game
# 3. The real killer: you don't know your edge (estimation error)
# 4. From coins to markets: Kelly leverage = mu / sigma^2, and max growth = Sharpe^2 / 2
#
# RULE: write your prediction for each part in prediction-sheet.md BEFORE you run it.
# Run: python kelly_lab.py   (or open in VS Code / Jupyter: the "# %%" lines are cells)

# %%
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)
fig, ax = plt.subplots(2, 2, figsize=(13, 9))

# %% [markdown]
# ## 1. The growth curve
# Even-money bet, win probability p. Bet a fraction f of your wealth each time.
# Expected log growth per bet: g(f) = p*ln(1+f) + (1-p)*ln(1-f)
# Kelly fraction f* = p - (1-p) = 2p - 1 (for even money). General odds b:1 -> f* = (b*p - q)/b

# %%
p = 0.60
f_star = 2 * p - 1
g = lambda f: p * np.log1p(f) + (1 - p) * np.log1p(-f)
fs = np.linspace(0, 0.6, 601)
print("=== 1. Growth curve, p = 0.60, even money ===")
print(f"Kelly fraction f* = {f_star:.2f}")
for mult in [0.25, 0.5, 1, 1.5, 2, 2.5]:
    f = mult * f_star
    print(f"  {mult:>4}x Kelly (bet {f:.0%}): growth per bet = {g(f):+.4f}  "
          f"({g(f)/g(f_star):.0%} of max).  Expected value per bet still = +{f*(2*p-1):.3f} of wealth")
ax[0, 0].plot(fs, g(fs))
ax[0, 0].axhline(0, color="k", lw=0.8)
for mult, c in [(0.5, "tab:green"), (1, "tab:blue"), (2, "tab:red")]:
    ax[0, 0].axvline(mult * f_star, color=c, ls="--", label=f"{mult}x Kelly ({mult*f_star:.0%})")
ax[0, 0].set_title("1. Growth rate vs bet size (p=0.6, even money)\nHalf Kelly: 75% of the growth. 2x Kelly: about zero.")
ax[0, 0].set_xlabel("fraction of wealth bet each flip"); ax[0, 0].set_ylabel("expected log growth per flip")
ax[0, 0].legend()

# %% [markdown]
# ## 2. Full vs half vs 2x Kelly to ruin
# Haghani & Dewey (2016): $25 start, coin with p = 0.6, about 300 flips in 30 minutes.
# (They also capped winnings at $250; we leave the cap off to see the raw shape.)
# "Ruined" here = wealth falls below $0.25 (1% of start): you can't come back in any useful time.

# %%
START, FLIPS, PLAYERS = 25.0, 300, 10_000
flips = rng.random((PLAYERS, FLIPS)) < p           # same coin flips for every strategy: fair comparison
print("\n=== 2. 10,000 players, 300 flips, $25 start ===")
print(f"{'strategy':>14} | {'median $':>10} | {'mean $':>12} | {'P(end < $25)':>12} | {'P(lose 50%+ at some point)':>26} | {'P(ruin)':>8}")
for mult, c in [(0.5, "tab:green"), (1.0, "tab:blue"), (2.0, "tab:red"), (3.0, "tab:purple")]:
    f = mult * f_star
    factors = np.where(flips, 1 + f, 1 - f)
    paths = START * np.cumprod(factors, axis=1)
    final = paths[:, -1]
    dd50 = (paths.min(axis=1) <= START * 0.5).mean()
    ruin = (paths.min(axis=1) < START * 0.01).mean()
    print(f"{str(mult)+'x Kelly':>14} | {np.median(final):>10.0f} | {final.mean():>12.0f} | {(final<START).mean():>12.1%} | {dd50:>26.1%} | {ruin:>8.1%}")
    med_path = np.median(paths, axis=0)
    ax[0, 1].plot(np.arange(1, FLIPS + 1), med_path, color=c, label=f"{mult}x Kelly (median path)")
    ax[0, 1].fill_between(np.arange(1, FLIPS + 1), np.percentile(paths, 10, axis=0),
                          np.percentile(paths, 90, axis=0), color=c, alpha=0.12)
ax[0, 1].set_yscale("log"); ax[0, 1].axhline(START, color="k", lw=0.8)
ax[0, 1].set_title("2. Median wealth (lines) and 10-90% band\nOver-betting: huge mean, miserable median")
ax[0, 1].set_xlabel("flip"); ax[0, 1].set_ylabel("wealth, $ (log scale)"); ax[0, 1].legend(fontsize=8)
print("Over-betting gives a giant MEAN and a collapsing MEDIAN. The mean rests on a handful of lucky paths (at 3x even\n"
      "the simulated mean is noise: rerun with another seed and watch it jump). You live the median, not the mean.")

# %% [markdown]
# ## 3. You don't know your edge
# You estimate p = 0.60 and bet full Kelly (20%). But the true p is lower.
# Kelly punishes over-betting much more than under-betting. This is the real reason pros use half Kelly or less.

# %%
print("\n=== 3. Estimation error: you think p = 0.60 ===")
true_ps = np.linspace(0.50, 0.65, 151)
for name, f in [("full Kelly on estimate (20%)", 0.20), ("half Kelly on estimate (10%)", 0.10)]:
    gr = true_ps * np.log1p(f) + (1 - true_ps) * np.log1p(-f)
    ax[1, 0].plot(true_ps, gr, label=name)
    for tp in [0.55, 0.53]:
        gg = tp * np.log1p(f) + (1 - tp) * np.log1p(-f)
        print(f"  {name}: if true p = {tp}, growth per bet = {gg:+.4f}")
best = true_ps * np.log1p(2*true_ps-1) + (1-true_ps) * np.log1p(-(2*true_ps-1))
ax[1, 0].plot(true_ps, best, "k--", label="if you knew the true p")
ax[1, 0].axhline(0, color="k", lw=0.8)
ax[1, 0].set_title("3. Bet sized on p=0.60, but the true p is...\nFull Kelly goes NEGATIVE if true p < 0.55")
ax[1, 0].set_xlabel("true win probability"); ax[1, 0].set_ylabel("growth per bet"); ax[1, 0].legend(fontsize=8)

# %% [markdown]
# ## 4. From coins to markets
# Continuous version (Thorp 2006, sec. 7): for an asset with excess return mu and volatility sigma,
#   Kelly leverage  L* = mu / sigma^2
#   growth at L:    g(L) = r + L*mu - L^2 * sigma^2 / 2
#   max growth      g* = r + Sharpe^2 / 2
# The numbers below are ILLUSTRATIVE ASSUMPTIONS, not forecasts. Day 4 you'll measure sigma on real NIFTY data.

# %%
print("\n=== 4. Coins to markets (illustrative assumptions) ===")
sigma = 0.16
r = 0.0
for mu in [0.02, 0.04, 0.06]:
    L = mu / sigma**2
    print(f"  assumed excess return {mu:.0%}, vol {sigma:.0%}: Sharpe {mu/sigma:.2f}, Kelly leverage {L:.2f}x, "
          f"max growth {(mu/sigma)**2/2:.2%}/yr")
Ls = np.linspace(0, 5, 501)
for mu, c in [(0.02, "tab:red"), (0.04, "tab:orange"), (0.06, "tab:green")]:
    ax[1, 1].plot(Ls, r + Ls * mu - Ls**2 * sigma**2 / 2, color=c, label=f"assumed mu={mu:.0%}, vol 16%")
ax[1, 1].axhline(0, color="k", lw=0.8)
ax[1, 1].set_ylim(-0.08, 0.08)
ax[1, 1].set_title("4. Growth vs leverage on an index\nIf you guess mu=6% but it's 2%, 2.3x leverage loses money")
ax[1, 1].set_xlabel("leverage (1 = fully invested, no borrowing)"); ax[1, 1].set_ylabel("growth per year"); ax[1, 1].legend(fontsize=8)
print("  Lesson: the formula is exact; your inputs are not. A mu error of a few % flips the answer from 'lever up' to 'don't'.")

plt.tight_layout(); plt.savefig("kelly_lab.png", dpi=120)
print("\nSaved: kelly_lab.png")

# %% [markdown]
# ## Questions for your log
# 1. Part 1: in one sentence, why does 2x Kelly have about zero growth even though every bet has positive EV?
# 2. Part 2: which column would a salesman show you (mean or median)? Which one do YOU live through?
# 3. Part 3: if your backtest says p = 0.60 from 100 trades, what's the standard error of p? (Hint: Day 2, sqrt(p(1-p)/n).)
#    What fraction of Kelly does that uncertainty justify?
# 4. Part 4: write your own sizing rule for the strategy you'll build in Week 3, BEFORE you know its backtest.
#    (Suggestion: target volatility, capped at 1x leverage, and no more than half Kelly on a deliberately pessimistic edge.)
