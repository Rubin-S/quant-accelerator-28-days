# DAY 7: Fri 6 Nov 2026
## The NSE cost stack + GATE 1

Yesterday you learned the costs you can't see: spread, adverse selection, impact. Today it's the costs you CAN see, which retail traders still ignore: STT, exchange charges, SEBI fee, stamp duty, GST, DP charges, and the tax on your gains.

The idea in one line: **a strategy's edge is what's left after the government, the exchange, the depository and your broker have been paid.** SEBI's 2024 study found 71% of individual intraday traders in the cash segment lost money in FY23, and for the loss-makers, trading costs added another 57% on top of their trading losses (in 08_research).

**Deliverable (from the plan):** a cost calculator in code, checked to within 20% of a real contract note. Then **GATE 1**.

---

## Your day (about 6 h; deep work about 4 h)

| Time | Block | What | Files |
|---|---|---|---|
| 30 min | Drill | Zetamac + market-making game. Log scores. | |
| 45 min | Deep 1: Sources first | Read `RATES_SNAPSHOT`, then open each official PDF it cites and find the number yourself: NSE/FA/73061 (transaction charge), the BSE Apr 2026 STT table, the SEBI stamp-duty FAQ. **Don't trust my table: verify it.** | 01_official_rates/ |
| 75 min | Deep 2: Build | BEFORE opening `nse_costs.py`, write your own calculator from the sources (functions for one leg and a round trip; delivery/intraday; share/equity ETF/gold ETF). Then compare it with mine and run `test_nse_costs.py` against yours. Add ≥3 tests of your own. | 04_build_along/ |
| 30 min | Deep 3: Reality check | `contract_note_check.py` against a REAL contract note. No account yet? Price the same trade on your broker's official brokerage calculator and save a screenshot. Explain every line that differs. | 04_build_along/ |
| 45 min | Deep 4: Costs vs a strategy | Fill `prediction-sheet.md` → run `cost_drag_lab.py` (costs and tax applied to two toy MA rules on real NIFTYBEES data) → answer its 6 questions. Log both rules in your trial log. | 04_build_along/ |
| 45 min | Problems | The 10 problems, by hand first. | 05_problems/ |
| 30 min | **GATE 1** | Go through `GATE_1_CHECKLIST.md` honestly, then send me everything. | 07_gate1/ |
| 15 min | Review | Training log row. | 06_templates/ |

**Setup:** `pip install numpy pandas matplotlib pytest`.

---

## Two data notes
- **New bad ticks found:** NIFTYBEES has one-day spikes on 2010-02-05 (+10.8%, then reversed) and 2010-10-06 (−15%, then reversed). Day 4's lab only removed the 2019 glitch. It doesn't change Day 4's CAGR (that uses only the endpoints), but it slightly affects NIFTYBEES volatility and correlation numbers. The lab filters these spikes; Day 14's audit will hunt them properly.
- **The toy MA rules are not ideas.** They exist only to show what costs do. Both trail buy-and-hold by ~6 CAGR points before a single rupee of cost. That's a lesson too.

---

## What to take from the research (08_research)
- **SEBI 2024, intraday trading in the cash segment:** the Indian evidence. Read the summary (pp. 3–4).
- **Novy-Marx & Velikov (2016):** most anomalies with turnover above 50% a month die after costs. A "buy/hold spread" (stricter rules to enter than to stay) is the best cheap fix. You'll use that idea in Week 2.
- **Frazzini, Israel & Moskowitz:** institutional costs are far lower than academic estimates assume. You are not an institution: your fixed fees (DP charge) and tax matter more than impact.

---

## Mentor's rules for Day 7 (permanent)
1. **Every rate has a source and a date.** If you can't cite it, it's not in the model.
2. **Costs are computed per order, from the broker's actual rules,** never as a single "0.1%" guess.
3. **Tax is a cost.** Short-term gains on equity are taxed at 20% (+cess). A strategy that turns everything into short-term gains needs to earn that back.
4. **Compare like with like.** Before "fixing" your model against a contract note, check you're comparing the same items (DP charges aren't on Zerodha's note).

Send me: your calculator + tests, the contract-note check output, the lab predictions vs actuals + 6 answers, the 10 problems, and the Gate 1 checklist with your honest verdict.
