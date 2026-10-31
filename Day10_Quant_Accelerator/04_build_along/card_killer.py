# %% [markdown]
# # Day 10 build-along: THE CARD KILLER
# The mentor's kill session, as code. Every idea card goes through 6 screens. Each screen asks one question
# a desk head would ask before giving you a rupee. Put YOUR cards in my_cards.csv (same columns as demo_cards.csv).
#
# Screens (in order; the first KILL is final):
# S1 House rules: F&O, shorting or leverage > 1.0x?                              -> KILL
# S2 Payer: no believable "who pays me and why" story?                          -> KILL
# S3 Evidence sign: our exploration t is NEGATIVE (wrong way)?                  -> KILL
# S4 Costs: edge after literature haircut minus Day 7 costs <= 0?               -> KILL
#           edge after haircut < 2x costs (one bad fill wipes it)?             -> PARK (too thin)
# S5 Complexity: more than 3 tunable parameters?                                -> PARK (simplify first)
# S6 Testability: can we ever reach t >= 3?
#           - Discovery mode: years needed = (3 / net Sharpe)^2 must be <= 12 (our 2007-2018 window)
#           - Confirm mode: literature already shows t >= 3 elsewhere; our job is only to confirm, not discover
#           Neither -> PARK (can't be proven with our data)
# Overlays (risk tools like Faber) skip the edge screens; they're judged on cost and complexity only.
#
# Haircuts (McLean & Pontiff 2016, Day 8): returns are about 26% lower out-of-sample and 58% lower after
# publication. So we keep 42% of a published edge and 74% of an unpublished one.
# Demo numbers: rough guesses built from Day 8 explorer results and the papers. They are NOT facts. Replace them with yours.

# %%
import sys, math, pandas as pd
from pathlib import Path
from nse_costs import round_trip
HERE = Path(__file__).resolve().parent if "__file__" in globals() else Path(".")
CAPITAL, SPREAD_BPS_PER_SIDE, YEARS_AVAILABLE, TAX = 1e5, 5.0, 12, 0.208   # 20% STCG + 4% cess

def cost_bps(instrument, product):
    return round_trip(CAPITAL, CAPITAL, product, instrument)["total"] / CAPITAL * 1e4 + 2 * SPREAD_BPS_PER_SIDE

def judge(c):
    notes, verdict = [], "SURVIVE"
    cb = cost_bps(c.instrument, c["product"])
    keep = 0.42 if c.published else 0.74
    net = c.gross_edge_bps_per_trade * keep - cb
    annual = net * c.trades_per_year / 100                       # % a year, pre-tax
    after_tax = annual * (1 - TAX) if (c.avg_hold_days < 365 and annual > 0) else annual
    def out(v, why):
        return dict(verdict=v, reason=why, cost_bps=round(cb, 1), net_bps_trade=round(net, 1),
                    net_pct_yr=round(annual, 2), after_tax_pct_yr=round(after_tax, 2))
    if c.needs_short_or_fo or c.leverage > 1.0:
        return out("KILL", "S1 breaks house rules (short/F&O/leverage)")
    if not c.has_payer:
        return out("KILL", "S2 no payer story")
    if pd.notna(c.our_t) and c.our_t < 0:
        return out("KILL", f"S3 our data points the wrong way (t = {c.our_t})")
    if c.card_type == "overlay":
        yearly_cost = cb * c.trades_per_year / 100
        if c.n_params > 3:
            return out("PARK", "S5 too many knobs")
        r = out("SURVIVE", f"overlay: costs about {yearly_cost:.2f}% a year; judge it on drawdown, not return")
        r.update(net_bps_trade=None, net_pct_yr=None, after_tax_pct_yr=None)
        return r
    if net <= 0:
        return out("KILL", f"S4 costs eat it: {c.gross_edge_bps_per_trade} bps gross x {keep} haircut < {cb:.1f} bps cost")
    if net < 2 * cb:
        return out("PARK", f"S4 too thin: net {net:.1f} bps vs cost {cb:.1f} bps (needs > 2x)")
    if c.n_params > 3:
        return out("PARK", "S5 more than 3 parameters: simplify first")
    sr_net = c.expected_sharpe_gross * net / c.gross_edge_bps_per_trade if c.gross_edge_bps_per_trade else 0
    yrs = (3 / sr_net) ** 2 if sr_net > 0 else math.inf
    if pd.notna(c.external_t) and c.external_t >= 3:
        return out("SURVIVE", f"confirm mode: literature t >= 3; we only need a same-sign confirmation (discovery would need {yrs:.0f} yrs)")
    if yrs <= YEARS_AVAILABLE:
        return out("SURVIVE", f"discovery mode: t = 3 reachable in {yrs:.0f} yrs")
    return out("PARK", f"S6 untestable: needs about {yrs:.0f} years of data to reach t = 3, we have {YEARS_AVAILABLE}")

f = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else HERE / "demo_cards.csv"
cards = pd.read_csv(f)
res = pd.DataFrame([judge(c) for _, c in cards.iterrows()])
table = pd.concat([cards[["name"]], res], axis=1)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 95)
print(f"Cards from {f.name}. Cost assumes Rs 1 lakh per trade + {SPREAD_BPS_PER_SIDE:.0f} bps spread per side.\n")
print(table[["name", "verdict", "cost_bps", "net_bps_trade", "after_tax_pct_yr"]].to_string(index=False))
print("\nReasons:")
for _, r in table.iterrows():
    print(f"  [{r.verdict:7}] {r['name']}: {r.reason}")
print("\nCount:", table.verdict.value_counts().to_dict())
table.to_csv(HERE / f"verdicts_{f.stem}.csv", index=False)

# %% [markdown]
# ## How to use it in the kill session
# 1. Copy demo_cards.csv to my_cards.csv and enter your 10 cards. Be honest: gross edge and Sharpe are YOUR prior,
#    taken from papers or Day 8 numbers, never from 2019+ data.
# 2. Run `python card_killer.py my_cards.csv`.
# 3. For every KILL, write one line in your defence or accept the death. For every PARK, write what would un-park it.
# 4. The script is a FILTER, not a judge. I'll still attack the survivors on payer logic and on whether the
#    numbers you typed are believable. Garbage in, survivor out.
