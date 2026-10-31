# DAY 5: Wed 4 Nov 2026
## Overfitting: noise strategies, deflated Sharpe, minimum backtest length

Today is the most important defensive day of the 28. Almost every retail "quant strategy" dies of what you learn today.

The idea in one line: **if you try enough things, one will look brilliant by luck, and it will die the day you trade it.**
You'll prove it with your own hands, on real NIFTY data: 20 coin-flip strategies, crown a champion, watch it collapse.

Then you get three tools to defend yourself:
1. **Deflated Sharpe Ratio (DSR):** "Is this Sharpe still impressive, given how many things I tried?"
2. **Minimum Backtest Length (MinBTL):** "Do I even have enough data for this many tries?"
3. **Probability of Backtest Overfitting (PBO via CSCV):** "Does picking the in-sample winner beat a coin flip out of sample?"

And the habit that matters more than any formula: **count every trial.**

**Deliverable (from the plan):** proof that the best noise strategy is fake = `overfitting_lab` run with predictions first, plus the 10 problems, plus your trial log started properly.

---

## Your day (about 6 h; deep work about 4 h)

| Time | Block | What | Files |
|---|---|---|---|
| 30 min | Drill | Zetamac 2×2 + market-making game, 5 rounds. Log both. | |
| 30 min | Deep 0: Do it yourself first | Before opening my lab: in 20 lines of numpy, make 20 random +1/−1 signals on NIFTY returns, compute Sharpe on the first 70%, pick the best, check the last 30%. Write down what you expected first. | 03_data/ |
| 75 min | Deep 1: Read | **Bailey, Borwein, López de Prado & Zhu (2014)**, *Pseudo-Mathematics and Financial Charlatanism*: sections 1–3 (MinBTL; the key figure is how the best Sharpe grows with trials). Then **Bailey & López de Prado (2014)**, *The Deflated Sharpe Ratio*: sections 1–4 (the False Strategy Theorem + the DSR formula). | 01_core_papers/ |
| 75 min | Deep 2: Lab | Fill `prediction-sheet.md` → run `overfitting_lab.py` → answer its 5 questions. Then question 5's experiment: rerun on the last 2 years only. | 04_build_along/ |
| 60 min | Deep 3: Problems | 10 problems. Then set up `trial-log-template.md` and log every backtest you've run so far in this program (yes, including Day 4's). | 05_, 06_ |
| 45–60 min | Light | Video: López de Prado, *Dangers of Backtest Overfitting*. Then Harvey & Liu, *Evaluating Trading Strategies* (11 pages, very readable). | RESOURCES.md, 02_ |
| 15 min | Review | Training log row | |

**Setup:** `pip install numpy pandas matplotlib scipy`. The CSV is in `03_data/` (the same NIFTY file as Day 4).

---

## What to pull from each reading

**Pseudo-Mathematics (Bailey et al. 2014):** with 45 independent tries you need about 5 years of data just to expect the best fake Sharpe to stay below 1. Most retail backtests try more than that on less data.

**Deflated Sharpe (2014):** the "expected maximum Sharpe" of N zero-skill strategies becomes your new zero. DSR is the probability your Sharpe beats *that*, adjusted for fat tails and sample length.

**Probability of Backtest Overfitting (2017):** skim sections 1–3 for the CSCV idea. The lab implements it in 15 lines.

**Harvey, Liu & Zhu (2016):** read only the intro and the conclusion. With hundreds of factors already tested, a new one needs **t > 3**, not 2. That's where our t > 3 rule comes from.

**Ioannidis (2005):** 6 pages from medicine, the same disease. Read it as a warning about yourself.

---

## Mentor's rules for Day 5 (permanent from today)
1. **Every backtest you look at is a trial. Log it.** Including bugs, peeks and "quick checks".
2. **The grid is fixed before you see results.** Small: think about 10–20 variants, not 1,000.
3. **Report DSR and the trial count next to every Sharpe.** A Sharpe without its N is meaningless.
4. **A holdout is used once.** Peek and tweak, and it's in-sample forever.
5. **Being ruthless with your own ideas is not pessimism.** It's the job.

Send me: what you predicted in Deep 0 before coding, lab predictions vs actuals, the 5 lab answers, the 10 problems, and your trial log with its current N.
