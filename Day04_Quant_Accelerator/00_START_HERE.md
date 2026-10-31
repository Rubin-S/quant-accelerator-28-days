# DAY 4: Tue 3 Nov 2026
## Real NIFTY data: log returns, volatility, correlation, fat tails

Days 1–3 used coins and dice. Today you touch the real thing: **19 years of NIFTY, in this ZIP.**
The point isn't the statistics. It's learning what the market actually looks like, so you never again size a bet or set a risk limit from a textbook bell curve.

Four stylized facts (Cont 2001) to see in your own numbers:
1. **Returns barely autocorrelate.** Direction is hard to predict.
2. **Volatility clusters.** Calm stays calm, storms stay stormy. Risk IS partly predictable.
3. **Fat tails.** 4-sigma days happen about 100x more often than a normal curve says.
4. **Correlations move,** and they're often highest when you need them lowest.

Plus one lesson that isn't in any paper: **free data lies.** There's a real error in this data. Find it before the lab shows you.

**Deliverable (from the plan):** stats notebook on 10+ years of NIFTY = `nifty_stats_lab` run with predictions first, plus the 10 problems and your data-audit checklist v0.

---

## Your day (about 6 h; deep work about 4 h)

| Time | Block | What | Files |
|---|---|---|---|
| 30 min | Drill | Zetamac 2×2 + market-making game, 5 rounds. Log both. | |
| 20 min | Deep 0: Raw audit | Before ANY code from me: open `NIFTYBEES_daily.csv` in pandas, plot Close, look for anything impossible. Write down what you find. | 03_data/ |
| 75 min | Deep 1: The facts | Cont (2001): sections 1–3 and 5 (the list of stylized facts, plus the tails and volatility clustering). Skim the math. Then Engle, *GARCH 101*: pages 1–8 only, the idea of volatility that changes over time. | 01_, 02_ |
| 75 min | Deep 2: Lab | Fill `prediction-sheet.md`, run `nifty_stats_lab.py` (or `.ipynb`), answer its 5 questions. **This is the Day 4 deliverable.** Then change one thing yourself: e.g. Bank Nifty instead of NIFTY, or 63-day instead of 21-day vol. | 04_build_along/ |
| 60 min | Deep 3: Problems | 10 problems on the real numbers. Then start `data-audit-checklist.md`. | 05_, 06_ |
| 45–60 min | Light | MIT 18.S096 *Volatility Modeling* lecture, the QuantEcon heavy-tails lecture, and the Taleb chapter 1 "non-technical overview" (first ~25 pages only). | RESOURCES.md |
| 15 min | Review | Training log row | |

**Setup:** `pip install numpy pandas matplotlib scipy` (plus `jupytext` if you want to rebuild the notebook). Keep the folder structure; the lab reads `../03_data/`.

---

## What to pull from each reading

**Cont (2001):** a checklist of what any model of returns must reproduce. For each fact, find the matching number in your lab output.

**Engle, GARCH 101:** today's vol is a weighted mix of the long-run average, yesterday's surprise and yesterday's vol. You won't fit GARCH today; you only need the idea that *recent vol predicts near-future vol.*

**Engle's Nobel lecture (optional):** the same idea from its inventor, with VaR and why risk management needs it.

**Taleb, Statistical Consequences of Fat Tails:** 500+ pages; read only the opening overview. The key line for a trader: under fat tails, the sample mean and the sample variance are unreliable, and your worst day hasn't happened yet.

**QuantEcon, Heavy-Tailed Distributions:** Python, hands-on, and it uses market data too. Do the exercises if you finish early.

---

## Mentor's rules for Day 4
1. **Audit before analysis, every time.** Plot raw prices with your eyes before computing anything.
2. **Never trust a normal sigma for a risk limit.** Use the worst day in the data, and assume a worse one is coming.
3. **Write the IST timestamp at which every input becomes known.** Most fake backtests die here.
4. **Benchmark against what you could actually hold** (TRI or the ETF), never the price index.

Send me: what you found in the raw audit (before reading the lab), lab predictions vs actuals, the 5 lab answers, the 10 problems, and your audit checklist.
