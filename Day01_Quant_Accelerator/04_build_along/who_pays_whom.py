"""
Day 1 build-along: WHO PAYS WHOM?
A tiny market with three kinds of players (Bagehot/Treynor 1971, Glosten-Milgrom 1985):
  - informed traders : know the true value, trade only when it helps them
  - noise traders    : trade for reasons unrelated to value (need cash, boredom, tips)
  - market maker     : quotes bid/ask, must survive both

Part A  - run the market, see where the money goes.
Part B  - a retail trader with ZERO edge who pays costs. How many lose, and how does
          that change with the number of trades? Compare to SEBI's intraday study.

Run:  python who_pays_whom.py      (needs numpy, matplotlib)
Your job after running: change the knobs at the top, predict first, then run.
Write predictions in your training log BEFORE you run. Grade yourself on the prediction.
"""
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)

# ---------------- knobs (change these) ----------------
N_ROUNDS        = 200_000   # trades in the market
P_INFORMED      = 0.20      # share of order flow that is informed
VALUE_JUMP      = 1.00      # true value is V0 +/- this each round
HALF_SPREAD     = None      # None = market maker sets the break-even (Glosten-Milgrom) spread

# ---------------- Part A: the market ----------------
def break_even_half_spread(p_inf, jump):
    # MM loses `jump - s` to every informed trade, earns `s` from every noise trade.
    # Break-even: p_inf*(jump - s) = (1-p_inf)*s  ->  s = p_inf*jump
    return p_inf * jump

s = break_even_half_spread(P_INFORMED, VALUE_JUMP) if HALF_SPREAD is None else HALF_SPREAD

pnl = {"informed": 0.0, "noise": 0.0, "market_maker": 0.0}
for_plot = {k: [] for k in pnl}
is_inf  = rng.random(N_ROUNDS) < P_INFORMED
v_up    = rng.random(N_ROUNDS) < 0.5            # true value goes up or down
noise_buy = rng.random(N_ROUNDS) < 0.5

for t in range(N_ROUNDS):
    true_move = VALUE_JUMP if v_up[t] else -VALUE_JUMP     # value relative to mid
    if is_inf[t]:
        buy = v_up[t]                                     # informed buy only if value rises
        who = "informed"
    else:
        buy = noise_buy[t]
        who = "noise"
    # trader buys at mid+s, or sells at mid-s; payoff measured against true value
    # buy : pays (mid + s), receives asset worth (mid + true_move)  -> true_move - s
    # sell: receives (mid - s), gives asset worth (mid + true_move) -> -true_move - s
    trader_pnl = (true_move - s) if buy else (-true_move - s)
    pnl[who] += trader_pnl
    pnl["market_maker"] -= trader_pnl                     # zero-sum before costs
    if t % 1000 == 0:
        for k in pnl: for_plot[k].append(pnl[k])

print("=== Part A: who pays whom ===")
print(f"informed share={P_INFORMED:.0%}  half-spread={s:.3f}")
for k, v in pnl.items():
    print(f"{k:13s} total P&L = {v:12,.0f}")
print("Sum of all P&L (zero-sum check):", round(sum(pnl.values()), 6))

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
x = np.arange(len(for_plot["informed"])) * 1000
for k, c in zip(pnl, ["tab:green", "tab:red", "tab:blue"]):
    ax[0].plot(x, for_plot[k], label=k, color=c)
ax[0].axhline(0, color="k", lw=0.5)
ax[0].set_title("Part A: noise traders pay informed traders,\nthe market maker just passes it through")
ax[0].set_xlabel("trades"); ax[0].set_ylabel("cumulative P&L"); ax[0].legend()

# ---------------- Part B: zero-edge retail trader paying costs ----------------
# Each trade: gross return ~ N(0, sigma) (no edge), minus round-trip cost.
N_TRADERS   = 20_000
SIGMA       = 0.010     # 1% typical move per trade
COST        = 0.0005    # 0.05% round trip (brokerage+STT+exchange+GST+stamp+slippage). Rough guess - you compute the real one on Day 7
trade_counts = [10, 50, 100, 250, 500, 1000, 2000]
loser_share = []
for n in trade_counts:
    gross = rng.normal(0.0, SIGMA, size=(N_TRADERS, n)).sum(axis=1)
    net = gross - COST * n
    loser_share.append((net < 0).mean())
    
print("\n=== Part B: zero edge + costs ===")
for n, l in zip(trade_counts, loser_share):
    print(f"{n:5d} trades/yr -> {l:5.1%} of traders lose")
print("SEBI FY23 intraday cash study: 71% lost overall, 80% among traders with >500 trades/yr.")
print("Note: this toy assumes ZERO skill for everyone. Real traders vary, so the curve is a shape, not a fit.")

ax[1].plot(trade_counts, np.array(loser_share) * 100, "o-", color="tab:red", label="zero-edge simulation")
ax[1].axhline(71, ls="--", color="gray"); ax[1].text(12, 72, "SEBI intraday: 71% lose", color="gray")
ax[1].axhline(80, ls=":", color="gray");  ax[1].text(12, 81, ">500 trades: 80% lose", color="gray")
ax[1].set_xscale("log"); ax[1].set_ylim(40, 100)
ax[1].set_xlabel("trades per year (log)"); ax[1].set_ylabel("% of traders who lose")
ax[1].set_title("Part B: no edge + costs = slow certain loss")
ax[1].legend(loc="lower right")
plt.tight_layout()
plt.savefig("who_pays_whom.png", dpi=130)
print("\nSaved chart: who_pays_whom.png")

# ---------------- Questions for your training log ----------------
# 1. Set P_INFORMED = 0.5. Predict the new half-spread and who gets hurt most. Run. Were you right?
# 2. Set HALF_SPREAD = 0.05 (MM quotes too tight). Predict MM P&L. Run.
# 3. In Part B, set COST = 0.0003. How many trades/yr before 70% lose? Why does cost matter more
#    the more you trade, while the luck (sigma) term grows only with sqrt(n)?
# 4. Which player are YOU by default when you click "buy" on an app? Which player do you want to be?
