# DAY 11: Tue 10 Nov 2026 (NSE shut): THE 8-POINT PAPER CHECKLIST
## Your Day 10 survivors face 8 checks. Any zero = dead. Tomorrow you pick ONE plus a backup.

Market's closed, so it's a desk day. On a real desk, this is the day you write the memo before anyone gives you money.

| Time | Block | What | Files |
|---|---|---|---|
| 20 min | Drill | Zetamac + "beta 0.4, NIFTY −20%: what does the overlay lose?" × 5 | |
| 40 min | Read (payer, P1) | Moskowitz–Ooi–Pedersen *Time Series Momentum* §1 + §6 (why it works) · Hurst–Ooi–Pedersen *Century of Evidence* (all 16 pages) · Asness et al. *Fact, Fiction and Momentum* (the 10 myths) | 01_ |
| 20 min | Read (costs, P2–3) | Frazzini–Israel–Moskowitz abstract + intro + conclusion: real costs are smaller than academics think, but capacity is finite | 02_ |
| 25 min | Read (beta, P4) | Agarwalla–Jacob–Varma (IIMA) §1–3: how India's factors are built. Then open the factor CSV in 09_data | 03_ |
| 15 min | Read (regimes, P6) | Daniel–Moskowitz *Momentum Crashes*, abstract + intro | 04_ |
| 10 min | Read (execution, P8) | NSE data-definitions PDF: Close vs LTP (the close is "averaging of trades over the last 30 minutes") | 05_ |
| 45 min | Run | `python checklist_scorer.py`. Predict each number first. Then add YOUR survivors | 06_build_along/ |
| 60 min | Write | One scoresheet per survivor (0/1/2 per point, a number per line) | 07_templates/ |
| 20 min | Problems | 10 problems | 08_problems/ |
≈ 4.3 h.

## What the scorer found on my two demo survivors (2008-07 to 2018-12, net of costs, daily data)
| | NIFTY hold | Faber 10m | 12m trend |
|---|---|---|---|
| CAGR | 9.91% | 8.34% | 5.91% |
| Max drawdown | −45.4% | −25.3% | −20.5% |
| Market beta (IIMA factors) | 1 | 0.43 | 0.28 |
| Alpha t-stat | n/a | −0.05 | −0.56 |
| Independent decisions | n/a | 11 spells | 10 spells |
| 2008 crash | −25.2% | +4.4% | +4.4% |
| Cost of a one-day delay | n/a | 0.27%/yr | 1.03%/yr |

**Reading:** both are drawdown overlays (part-time beta), not alpha. Both fail point 5 on our data, so they live only in
confirm mode. The 12-month version looks weaker and more timing-sensitive here. **Don't pick on that number alone;**
it's 10 decisions. The momentum ETF can't be tested pre-2019 at all (no ETF before 2022; backfilled index).
Note: Day 9's numbers differ slightly (monthly bars, no 1-day lag). Same story.

## Mentor's rules for Day 11
1. **A zero anywhere kills it.** No averaging away a fatal flaw.
2. **Every score needs a number.** "Seems liquid" scores 0; "₹3 cr ADV vs ₹1 lakh order" scores 2.
3. **Call an overlay an overlay.** Getting this right is worth more than any Sharpe ratio.
4. **2019+ stays locked.** Liquidity and launch dates are facts you may look up. Returns after 2018 are not.
5. **If nothing passes, say so.** That's a valid result; we'd fall back to a plain baseline and say so honestly (Gate 3 rule).

Send me: a scoresheet per survivor, the scorer output (+ your own survivors), the 10 problems, trial log (+2 trials for
the two demo variants if you run them), and your training-log row. Tomorrow (Day 12): pick one + backup and pre-register.
