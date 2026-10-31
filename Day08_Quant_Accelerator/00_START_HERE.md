# DAY 8: Sat 7 Nov 2026
## Edge families: where money actually comes from

Week 1 taught you how to lose less: costs, overfitting, sizing. Week 2 is about finding something worth testing.
Today's one question: **who pays me, and why do they keep paying?**

Six families cover almost every systematic edge:
| Family | The bet | Who pays | Founding evidence (in this ZIP) |
|---|---|---|---|
| Trend (time-series momentum) | What went up keeps going up for months | Hedgers, slow updaters | Moskowitz-Ooi-Pedersen 2012; Hurst-Ooi-Pedersen 2017 (since 1880) |
| Momentum (cross-sectional) | Winners beat losers | Under-reacting investors | Jegadeesh-Titman 2001; Asness-Moskowitz-Pedersen 2013; IIMA India factors |
| Mean reversion | Short-term overshoots snap back | Impatient traders paying for liquidity | Lo-MacKinlay 1990 |
| Carry | Earn the yield if nothing changes | Those buying insurance or certainty | Koijen-Moskowitz-Pedersen-Vrugt |
| Events / calendar / flows | Predictable flows move prices | Rule-bound traders (index funds, month-end) | Lou-Polk-Skouras 2019; India calendar studies (RESOURCES) |
| Pairs / relative value | Close substitutes drift apart and come back | Liquidity shocks in one leg | Gatev-Goetzmann-Rouwenhorst 2006 |

And the reality check: **McLean & Pontiff** found published anomalies earn 58% less after publication; **Lo's Adaptive Markets** explains why edges come and go.

**Deliverable: 3 idea cards** (template + my worked example in 08_templates).

---

## THE NEW RULE (permanent from today)
**All exploration uses data up to 2018-12-31 only. 2019–2026 is LOCKED** as your future out-of-sample test. The lab's loader enforces it.
Don't even look at a 2021 chart of your idea. Once seen, never clean again.

---

## Your day (about 6 h; deep work about 4 h)
| Time | Block | What | Files |
|---|---|---|---|
| 30 min | Drill | Zetamac + market-making game | |
| 75 min | Deep 1: Read | MOP 2012 (abstract, intro, Fig. 1, Sec. 4), Gatev et al. (intro + results), McLean-Pontiff (abstract + intro). Skim the rest: Hurst, Asness, Carry, Lou-Polk-Skouras, Lo. For each family, write: bet / payer / how it dies. | 01–05 |
| 30 min | Deep 2: India | Run `india_factor_facts.py`: India's academic factors from the IIMA library, including momentum's size, pain and era-by-era Sharpe. Skim the Nifty200 Momentum 30 methodology. | 04, 06 |
| 45 min | Deep 3: Explore | Predict first, then run `edge_family_explorer.py`: 8 pre-declared tests, one per family, 2007–2018 only, robust t-stats. **Add 8 to your trial log.** | 06 |
| 60 min | Deep 4: Cards | Write 3 idea cards. At least 2 families. Each must fit our rules (NSE cash ETFs/index, long/flat, 1.0×, no F&O) and carry a Day 7 cost estimate. | 08 |
| 45 min | Problems | The 10 problems | 07 |
| 15 min | Review | Training log row | |

---

## What the explorer found (so you know it's honest)
Nothing clears |t| > 3. The best three: overnight-minus-intraday on NIFTYBEES (t = 2.49), daily continuation in the index (robust t = 2.20; the naive t was 3.99) and turn-of-month (t = 2.00). With 8 tests, at least one |t| > 2 shows up by luck about 31% of the time. **These are clues for cards, not strategies.** And the BANK/NIFTY "pair" isn't a pair: 0.88 daily correlation, but a spread half-life of 403 days.

## Mentor's rules for Day 8 (permanent)
1. **No payer, no card.** A pattern without a reason is noise until proven otherwise, and you can't prove it with the same data.
2. **One parameter set, from the literature.** Never tune a card's numbers on data.
3. **Haircut every published edge by about half,** then subtract Day 7 costs and tax.
4. **Fit the rules or die:** NSE cash, index ETFs, long/flat, 1.0×, no F&O, no borrowing.
5. **The locked sample stays locked.**

Send me: 3 idea cards, explorer predictions vs actuals + 6 answers, the 10 problems, and your trial-log count.
