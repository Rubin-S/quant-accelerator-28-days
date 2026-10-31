# %% [markdown]
# # Day 5... no, Day 6 build-along: THE NAIVE MARKET MAKER THAT LOSES
# Deliverable: a naive market maker that loses, and an explanation of WHY, with numbers.
#
# Part A. A Glosten-Milgrom style market: a hidden true value, informed traders who know where it's going,
#         noise traders who trade for their own reasons. A naive MM quotes a fixed spread around a stale mid.
# Part B. Decompose its P&L: spread earned from noise traders vs adverse selection paid to informed traders.
# Part C. Markouts: how each fill looks 1, 10, 100 steps later. The professional's favourite diagnostic.
# Part D. The break-even spread vs the share of informed traders (Glosten-Milgrom intuition).
# Part E. Fix 1: learn from order flow (update mid on each trade). Fix 2: skew quotes on inventory (Avellaneda-Stoikov idea).
# Part F. Back to YOUR world: estimate the spread of NIFTYBEES from daily data (Roll 1984, Corwin-Schultz 2012),
#         and what it costs a strategy that trades N times a year.
# Part G. Export the session as a CSV for YOUR C++ orderbook replay tool.
# RULE: fill prediction-sheet.md first.

# %%
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from pathlib import Path
HERE = Path(__file__).resolve().parent if "__file__" in globals() else Path(".")
DATA = HERE.parent / "05_data"
TICK = 0.01

def simulate(n=20000, p_informed=0.15, half_spread=0.03, learn=0.0, skew=0.0, jump=0.05, p_jump=0.02,
             seed=1, record=False):
    """One market. True value V does a jump random walk (+/-jump with prob p_jump per step).
    Each step one trader arrives: informed with prob p_informed (knows V, buys if V > ask, sells if V < bid),
    else noise (buys or sells 50/50).
    MM quotes bid = m - h - skew*inv, ask = m + h - skew*inv, then (if learn>0) moves m toward the trade.
    Trades 1 unit. Returns P&L marked to TRUE value, and its parts."""
    rng = np.random.default_rng(seed)
    V = 100.0; m = 100.0; inv = 0; cash = 0.0
    spread_pnl = 0.0; adverse = 0.0; n_inf = n_noise = 0
    fills = []   # (t, side, price, informed?)
    Vpath = np.empty(n); invpath = np.empty(n); pnl = np.empty(n)
    for t in range(n):
        if rng.random() < p_jump:
            V += jump if rng.random() < 0.5 else -jump
        bid = round((m - half_spread - skew * inv) / TICK) * TICK
        ask = round((m + half_spread - skew * inv) / TICK) * TICK
        informed = rng.random() < p_informed
        side = 0
        if informed:
            side = 1 if V > ask else (-1 if V < bid else 0)      # informed only trade when it pays
        else:
            side = 1 if rng.random() < 0.5 else -1
        if side == 1:      # trader buys at our ask: we sell
            cash += ask; inv -= 1; px = ask
        elif side == -1:   # trader sells at our bid: we buy
            cash -= bid; inv += 1; px = bid
        if side != 0:
            # split this fill's value vs TRUE value into "half-spread vs our mid" and "our mid vs truth"
            spread_pnl += half_spread
            adverse += (m - V) * (-side) if True else 0          # selling below truth / buying above truth
            if informed: n_inf += 1
            else: n_noise += 1
            if record: fills.append((t, -side, px, informed))  # -side = our side (+1 we bought)
            if learn > 0: m += learn * side                     # a buy pushes our mid up, a sell down
        Vpath[t] = V; invpath[t] = inv; pnl[t] = cash + inv * V
    out = dict(pnl=pnl[-1], spread=spread_pnl, adverse=adverse, n_inf=n_inf, n_noise=n_noise,
               max_inv=np.abs(invpath).max(), pnl_path=pnl, inv_path=invpath, V=Vpath)
    if record: out["fills"] = fills
    return out

fig, ax = plt.subplots(2, 3, figsize=(17, 10))

# %% [markdown]
# ## A-B. The naive market maker: fixed 3-paisa half-spread, never updates its mid

# %%
naive = simulate(record=True)
print("=== A-B. NAIVE MM (half-spread 0.03, never learns, 15% informed) ===")
print(f"  Fills: {naive['n_noise']} vs noise traders, {naive['n_inf']} vs informed")
print(f"  Spread earned (half-spread x fills): {naive['spread']:+.2f}")
print(f"  P&L marked to true value:            {naive['pnl']:+.2f}")
print(f"  Max inventory: {naive['max_inv']:.0f} units  <- it never noticed the price had moved")
ax[0, 0].plot(naive["pnl_path"], label="naive MM P&L"); ax[0, 0].set_title("A. Naive MM P&L (marked to true value)")
ax2 = ax[0, 0].twinx(); ax2.plot(naive["V"], color="grey", alpha=0.4); ax2.set_ylabel("true value", color="grey")
ax[0, 1].plot(naive["inv_path"], color="purple"); ax[0, 1].set_title("A. Naive MM inventory: it gets run over")

# %% [markdown]
# ## C. Markouts
# For each fill: our P&L if we mark it to the TRUE value k steps later. Noise fills: about +half-spread.
# Informed fills: negative, and worse the longer you wait.

# %%
print("\n=== C. MARKOUTS (average P&L per fill, in paise) ===")
f = pd.DataFrame(naive["fills"], columns=["t", "our_side", "px", "informed"])
for k in [0, 1, 10, 100]:
    tk = np.minimum(f.t + k, len(naive["V"]) - 1)
    f[f"mo{k}"] = f.our_side * (naive["V"][tk] - f.px) * 100
mo = f.groupby("informed")[["mo0", "mo1", "mo10", "mo100"]].mean().rename(index={False: "noise", True: "informed"})
print(mo.round(2).to_string())
mo.T.plot(ax=ax[0, 2], marker="o"); ax[0, 2].axhline(0, color="k", lw=0.5)
ax[0, 2].set_title("C. Markouts: noise fills pay you, informed fills bleed you"); ax[0, 2].set_ylabel("paise per fill")

# %% [markdown]
# ## D. How wide must the spread be? Sweep half-spread x share of informed traders (an MM that learns a little;
# value jumps of 0.10 so news matters more)

# %%
print("\n=== D. BREAK-EVEN: P&L per 1,000 steps (MM learns 0.005/trade; value jumps 0.10) ===")
hs = [0.01, 0.02, 0.03, 0.05, 0.08]; ps = [0.0, 0.05, 0.15, 0.30]
grid = pd.DataFrame(index=[f"{p:.0%} informed" for p in ps], columns=[f"h={h}" for h in hs], dtype=float)
for p in ps:
    for h in hs:
        res = [simulate(n=10000, p_informed=p, half_spread=h, learn=0.005, jump=0.10, seed=s)["pnl"] for s in range(4)]
        grid.loc[f"{p:.0%} informed", f"h={h}"] = np.mean(res) / 10
print(grid.round(2).to_string())
for i, p in enumerate(ps):
    ax[1, 0].plot(hs, grid.iloc[i].values, "o-", label=f"{p:.0%} informed")
ax[1, 0].axhline(0, color="k", lw=0.5); ax[1, 0].legend(); ax[1, 0].set_xlabel("half-spread")
ax[1, 0].set_title("D. More informed traders -> you need a wider spread\n(P&L per 1,000 steps)")

# %% [markdown]
# ## E. Two fixes: learn from flow, and skew on inventory

# %%
print("\n=== E. FIXES (15% informed, half-spread 0.03; average of 8 seeds) ===")
cfgs = {"naive (no learning, no skew)": dict(learn=0.0, skew=0.0),
        "learn from flow (0.01 per trade)": dict(learn=0.01, skew=0.0),
        "skew on inventory only (0.005/unit)": dict(learn=0.0, skew=0.005),
        "learn + skew": dict(learn=0.01, skew=0.005)}
for name, c in cfgs.items():
    rs = [simulate(seed=s, **c) for s in range(8)]
    print(f"  {name:38s} P&L {np.mean([r['pnl'] for r in rs]):+8.2f}   avg max |inventory| {np.mean([r['max_inv'] for r in rs]):6.0f}")
    r0 = simulate(seed=1, **c); ax[1, 1].plot(r0["pnl_path"], label=name)
ax[1, 1].legend(fontsize=8); ax[1, 1].set_title("E. Same market, four market makers")

# %% [markdown]
# ## F. Your world: what does NIFTYBEES actually cost to trade? (from DAILY data only)
# Roll (1984): spread = 2*sqrt(-cov(dP_t, dP_{t-1})), when the covariance is negative.
# Corwin-Schultz (2012): from 2-day vs 1-day high/low ranges. Both are rough with daily data; treat as a ceiling-ish guess.

# %%
print("\n=== F. NIFTYBEES spread estimates from daily data ===")
b = pd.read_csv(DATA / "NIFTYBEES_daily.csv", index_col=0, parse_dates=True)
b = b[~b.index.isin(pd.to_datetime(["2019-12-19", "2019-12-20"]))]           # vendor glitch found on Day 4
b = b[(b.High >= b.Low) & (b.Low > 0) & (b.Volume > 0)].loc["2018":]

def corwin_schultz(df):
    hl = np.log(df.High / df.Low) ** 2
    beta = hl + hl.shift(-1)
    gamma = np.log(np.maximum(df.High, df.High.shift(-1)) / np.minimum(df.Low, df.Low.shift(-1))) ** 2
    k = 3 - 2 * np.sqrt(2)
    alpha = (np.sqrt(2 * beta) - np.sqrt(beta)) / k - np.sqrt(gamma / k)
    s = 2 * (np.exp(alpha) - 1) / (1 + np.exp(alpha))
    return s.clip(lower=0)            # negative 2-day estimates set to 0, as the authors suggest

cs = corwin_schultz(b).groupby(b.index.year).mean() * 1e4
dp = np.log(b.Close).diff()
roll = dp.groupby(b.index.year).apply(lambda x: 2 * np.sqrt(-x.autocorr() * x.var()) * 1e4 if x.autocorr() < 0 else np.nan)
tab = pd.DataFrame({"Corwin-Schultz (bps)": cs.round(1), "Roll (bps)": roll.round(1)})
print(tab.to_string())
med = float(np.nanmedian(cs.values))
last_px = float(b.Close.dropna().iloc[-1]); tick_bps = 0.01 / last_px * 1e4
print(f"  Median yearly Corwin-Schultz estimate: {med:.1f} bps.")
print(f"  Floor: one Rs 0.01 tick at Rs {last_px:.2f} = {tick_bps:.2f} bps. The two numbers are ~{med/tick_bps:.0f}x apart.")
print("  LESSON: daily-bar estimators get noisy and biased upward when the true spread is tiny next to daily volatility. On a very liquid ETF the true quoted spread is")
print("  probably a tick or two, but you DON'T KNOW until you watch the live book (Day 13, Kite). Never pick the")
print("  cost number that flatters your backtest. Run it at both ends and see if the edge survives.")
print("  Spread cost per round trip is about one full spread (half on the way in, half on the way out), before brokerage, STT, fees.")
for trades in [12, 52, 250]:
    print(f"  {trades:3d} round trips/yr: spread cost {trades*tick_bps/100:.2f}%/yr if 1 tick,  {trades*med/100:.1f}%/yr if the daily estimate were true")
ax[1, 2].bar(tab.index.astype(str), tab["Corwin-Schultz (bps)"], label="Corwin-Schultz")
ax[1, 2].plot(tab.index.astype(str), tab["Roll (bps)"], "ro-", label="Roll"); ax[1, 2].legend()
ax[1, 2].set_title("F. NIFTYBEES spread estimates from daily bars (bps)"); ax[1, 2].tick_params(axis="x", rotation=45)

plt.tight_layout(); plt.savefig(HERE / "naive_mm_lab.png", dpi=105); print("\nSaved naive_mm_lab.png")

# %% [markdown]
# ## G. Export a session for YOUR C++ orderbook (Rubin-S/orderbook, replay format)
# The naive MM rests a GTC bid and ask; each arriving trader sends an IOC. After each fill the MM re-quotes
# with fresh IDs. Prices in integer ticks (1 tick = 0.01). MM order IDs start at 1,000,000.
# Run:  ./build/debug/orderbook_replay naive_mm_session.csv > replay_out.txt
# Then: python3 pnl_from_replay.py replay_out.txt naive_mm_session_truth.csv

# %%
def export_session(n=2000, seed=3, half_spread=0.03, p_informed=0.15, path=HERE / "naive_mm_session.csv"):
    rng = np.random.default_rng(seed)
    V, m = 100.0, 100.0; mm_id = 1_000_000; tid = 1
    lines = ["# naive MM session: MM ids >= 1000000; trader IOCs below that"]
    bid_id = ask_id = None; truth = []
    def tk(x): return int(round(x / TICK))
    def quote():
        nonlocal mm_id, bid_id, ask_id
        if bid_id is not None: lines.append(f"CANCEL,{bid_id}")
        if ask_id is not None: lines.append(f"CANCEL,{ask_id}")
        bid_id, ask_id = mm_id, mm_id + 1; mm_id += 2
        lines.append(f"ADD,{bid_id},BUY,{tk(m-half_spread)},1,GTC")
        lines.append(f"ADD,{ask_id},SELL,{tk(m+half_spread)},1,GTC")
    quote()
    for t in range(n):
        if rng.random() < 0.02: V += 0.05 if rng.random() < 0.5 else -0.05
        informed = rng.random() < p_informed
        if informed:
            side = "BUY" if V > m + half_spread else ("SELL" if V < m - half_spread else None)
        else:
            side = "BUY" if rng.random() < 0.5 else "SELL"
        if side:
            px = tk(m + half_spread) if side == "BUY" else tk(m - half_spread)
            lines.append(f"ADD,{tid},{side},{px},1,IOC"); tid += 1
            quote()                                                # naive: same mid, fresh quotes
        truth.append((t, V))
    lines.append(f"CANCEL,{bid_id}"); lines.append(f"CANCEL,{ask_id}")
    path.write_text("\n".join(lines) + "\n")
    pd.DataFrame(truth, columns=["step", "true_value"]).to_csv(HERE / "naive_mm_session_truth.csv", index=False)
    print(f"\n=== G. Wrote {path.name}: {len(lines)} commands. Final true value {V:.2f} (MM mid stayed at {m:.2f}) ===")

export_session()

# %% [markdown]
# ## Questions for your log
# 1. Split the naive MM's loss into "spread earned" and "adverse selection". Which is bigger and why?
# 2. From the markouts table: why do informed fills look WORSE at 100 steps than at 1 step?
# 3. From the grid in D: what half-spread breaks even at 5% and at 15% informed? Why do real spreads widen before news?
#    Bonus: 30% informed loses LESS than 15% here. Find the reason in the code (hint: what does the MM learn from?).
# 4. In E, why does skewing on inventory help even without learning? What does it NOT fix?
# 5. You will NOT be a market maker on NSE. You'll be the one crossing the spread. Using F, how many round trips a year
#    can a strategy with a 4% yearly edge afford before costs eat half of it: (a) at 1 tick, (b) at 10 bps all-in, (c) at the daily estimate?
