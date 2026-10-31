"""
Day 2 build-along: COIN-FLIP LAB
Four experiments. Each one kills a belief that loses traders money.

  1. Same EV, different variance  -> why "positive EV" is not enough
  2. The streak trap              -> why small samples lie about patterns (Miller & Sanjurjo 2018)
  3. Luck vs skill (Bayes)        -> how much a great 12-month record should change your mind
  4. Sharpe ratio noise           -> how many years before a backtest means anything (Lo 2002)

RULE: before running each part, write your prediction in the training log. Then run.
Run:  python coin_flip_lab.py      (needs numpy, matplotlib)
"""
import itertools
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)
fig, axes = plt.subplots(2, 2, figsize=(13, 9))

# ---------------- 1. Same EV, different variance ----------------
# Bet A: win 100 with p=0.5, lose 80 with p=0.5          EV = +10, SD ~ 90
# Bet B: win 1000 with p=0.1, lose 100 with p=0.9          EV = +10, SD = 330
def ev_sd(outcomes, probs):
    o, p = np.array(outcomes, float), np.array(probs, float)
    ev = (o * p).sum(); sd = np.sqrt(((o - ev) ** 2 * p).sum()); return ev, sd
A = ([100, -80], [0.5, 0.5]); B = ([1000, -100], [0.1, 0.9])
print("=== 1. Same EV, different variance ===")
for name, (o, p) in [("A", A), ("B", B)]:
    ev, sd = ev_sd(o, p); print(f"Bet {name}: EV = {ev:+.1f}, SD = {sd:.1f}")
N_BETS, N_PEOPLE = 50, 10_000
for name, (o, p), c in [("A", A, "tab:blue"), ("B", B, "tab:orange")]:
    totals = rng.choice(o, size=(N_PEOPLE, N_BETS), p=p).sum(axis=1)
    print(f"  after {N_BETS} bets of {name}: {np.mean(totals<0):.1%} of people are DOWN money (EV says +{10*N_BETS})")
    axes[0, 0].hist(totals, bins=60, alpha=0.55, color=c, label=f"Bet {name}: {np.mean(totals<0):.0%} lose money")
axes[0, 0].axvline(0, color="k", lw=1)
axes[0, 0].set_title(f"1. Same EV (+10/bet), different variance\nP&L after {N_BETS} bets, 10,000 people")
axes[0, 0].set_xlabel("total P&L"); axes[0, 0].legend()

# ---------------- 2. Streak trap (Miller-Sanjurjo) ----------------
# Flip a fair coin 4 times. In each sequence, look at flips right after a Head.
# What fraction of those were Heads? Average that fraction across all sequences.
print("\n=== 2. The streak trap ===")
for n in [3, 4, 5, 10, 20]:
    if n <= 10:
        seqs = np.array(list(itertools.product([0, 1], repeat=n)))      # exact: all sequences
    else:
        seqs = rng.integers(0, 2, size=(400_000, n))                    # simulate long ones
    after_h = seqs[:, :-1] == 1
    nxt = seqs[:, 1:]
    counts = after_h.sum(axis=1)
    valid = counts > 0
    frac = (nxt * after_h).sum(axis=1)[valid] / counts[valid]
    print(f"  n={n:2d} flips: average P(H | previous H) measured per sequence = {frac.mean():.3f}  (true = 0.500)")
    if n == 4: frac4 = frac.mean()
ns = list(range(3, 31))
vals = []
for n in ns:
    seqs = rng.integers(0, 2, size=(200_000, n))
    after_h = seqs[:, :-1] == 1; counts = after_h.sum(axis=1); v = counts > 0
    vals.append(((seqs[:, 1:] * after_h).sum(axis=1)[v] / counts[v]).mean())
axes[0, 1].plot(ns, vals, "o-"); axes[0, 1].axhline(0.5, color="k", ls="--")
axes[0, 1].set_title("2. Streak trap: a FAIR coin looks 'mean-reverting'\nin short samples")
axes[0, 1].set_xlabel("flips per sequence"); axes[0, 1].set_ylabel("avg measured P(H | H)")

# ---------------- 3. Luck vs skill ----------------
# 1,000 traders. 5% are skilled (win a month with p=0.60), 95% are coin-flippers (p=0.50).
# Someone shows you 10+ winning months out of 12. How likely are they skilled?
print("\n=== 3. Luck vs skill ===")
N_TRADERS, MONTHS, PRIOR = 1000, 12, 0.05
from math import comb
def p_at_least(k, n, p): return sum(comb(n, j) * p**j * (1-p)**(n-j) for j in range(k, n+1))
for k in [8, 9, 10, 11]:
    like_s, like_l = p_at_least(k, MONTHS, 0.60), p_at_least(k, MONTHS, 0.50)
    post = like_s * PRIOR / (like_s * PRIOR + like_l * (1 - PRIOR))
    print(f"  >= {k}/12 winning months: P(skilled | record) = {post:.1%}   "
          f"(expected lucky traders with this record out of {N_TRADERS}: {like_l*(1-PRIOR)*N_TRADERS:.0f}, skilled: {like_s*PRIOR*N_TRADERS:.0f})")
skilled = rng.random(N_TRADERS) < PRIOR
wins = rng.binomial(MONTHS, np.where(skilled, 0.60, 0.50))
bins = np.arange(-0.5, MONTHS + 1.5)
axes[1, 0].hist(wins[~skilled], bins=bins, alpha=0.6, label="lucky coin-flippers (95%)")
axes[1, 0].hist(wins[skilled], bins=bins, alpha=0.9, label="skilled, p=0.60 (5%)")
axes[1, 0].set_title("3. Who has the best 12-month record?\nMostly the lucky, because there are more of them")
axes[1, 0].set_xlabel("winning months out of 12"); axes[1, 0].legend()

# ---------------- 4. Sharpe ratio noise ----------------
# Daily returns, true annual Sharpe 0 vs 0.5. Estimate Sharpe from 1, 3, 5, 10, 20 years.
print("\n=== 4. Sharpe ratio noise ===")
years = [1, 3, 5, 10, 20]; SIMS = 4000; DAYS = 252
for true_sr, c in [(0.0, "tab:gray"), (0.5, "tab:green")]:
    lo, mid, hi = [], [], []
    for y in years:
        mu_d = true_sr / np.sqrt(DAYS) * 0.01; r = rng.normal(mu_d, 0.01, size=(SIMS, y * DAYS))
        est = r.mean(axis=1) / r.std(axis=1) * np.sqrt(DAYS)
        lo.append(np.percentile(est, 5)); mid.append(np.median(est)); hi.append(np.percentile(est, 95))
        if true_sr == 0.0: print(f"  true SR 0.0, {y:2d} yrs: 90% of backtests show SR between {lo[-1]:+.2f} and {hi[-1]:+.2f}")
    axes[1, 1].fill_between(years, lo, hi, alpha=0.25, color=c, label=f"true SR {true_sr}: 90% band")
    axes[1, 1].plot(years, mid, "o-", color=c)
print("  Rule of thumb: t-stat ~ SR * sqrt(years). To get t > 2 with SR 0.5 you need ~16 years; t > 3 needs ~36.")
axes[1, 1].axhline(0, color="k", lw=0.8)
axes[1, 1].set_title("4. Estimated Sharpe vs years of data\n(one backtest is ONE draw from this band)")
axes[1, 1].set_xlabel("years of daily data"); axes[1, 1].set_ylabel("estimated annual Sharpe"); axes[1, 1].legend()

plt.tight_layout(); plt.savefig("coin_flip_lab.png", dpi=120)
print("\nSaved chart: coin_flip_lab.png")

# ---------------- Questions for your log ----------------
# 1. Part 1: raise N_BETS to 500. Predict the new % losing for A and B before running.
# 2. Part 2: explain IN WORDS why a fair coin shows P(H|H) < 0.5 per sequence. (Hint: read Miller & Sanjurjo p.1-3.)
#    Where could this bias sneak into a trading backtest that counts "what happens after an up day"?
# 3. Part 3: change PRIOR to 0.01 (skill is rare). What happens to P(skilled | 10/12)? What does that say about
#    the Telegram "guru" with a 10/12 record?
# 4. Part 4: your future backtest will use ~10 years of NIFTY ETF data. What true Sharpe would you need for t > 3?
