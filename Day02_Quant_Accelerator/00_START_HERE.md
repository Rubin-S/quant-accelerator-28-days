# DAY 2: Sun 1 Nov 2026
## Expected value, variance, Bayes, and how small samples lie

Yesterday you learned **who** pays whom. Today you learn the arithmetic of **whether** you're being paid, and how to avoid fooling yourself about it.

Three ideas, and every one comes back later:
1. **EV tells you the direction. Variance tells you whether you survive the trip.** (Day 3: Kelly)
2. **Bayes: evidence moves a belief in proportion to the base rate.** A great record from a big crowd is weak evidence. (Day 5: overfitting, Week 2: idea selection)
3. **Small samples are not miniature populations.** They are noisy, and sometimes biased. (Every backtest you'll ever run)

**Today's deliverable:** 10 problems solved (folder 05) + the coin-flip lab run with predictions written first (folder 04).

---

## Your day (about 6 h; deep work about 4 h)

| Time | Block | What | Files |
|---|---|---|---|
| 30 min | Drill | Zetamac 2 rounds of 2 min (log scores, compare to yesterday) + `make_a_market.py`, 5 rounds (log P&L) | 04_build_along/make_a_market.py |
| 75 min | Deep 1: Core tools | Jane Street *Probability & Markets* guide (all 13 pages). Then MIT 18.05 reading pp. 18–28 (Bayes) and pp. 29–60 (EV and variance; skim proofs, do the examples). Keep the Stat 110 cheatsheet open. | 01_core_probability/ |
| 60 min | Deep 2: Traps | Tversky & Kahneman 1971 (6 pp.) → Ioannidis 2005 (6 pp.) → Gigerenzer pp. 1–5 (natural frequencies) → Miller & Sanjurjo intro pp. 1–5 → Lo 2002, intro + Table 1 | 02_, 03_ |
| 60 min | Deep 3: Lab | Fill `prediction-sheet.md` part by part, THEN run `coin_flip_lab.py`. Answer the 4 questions at the bottom. | 04_build_along/, 06_templates/ |
| 60 min | Deep 4: Problems | The 10 problems: gut guess → worked answer → trading meaning. Open the solutions only at the end. | 05_problems/ |
| 45–60 min | Light | 3Blue1Brown on Bayes + the medical test paradox, Veritasium's *Bayesian Trap*. Optional: Stat 110 Lecture 4. | RESOURCES.md |
| 15 min | Review | Training log row (06_templates), trial log (still empty, good) | |

---

## What to pull from each reading (write one line per item in your notes)

**Jane Street guide:** expected value as a fair price; why market makers think in EV per trade; the adverse-selection question ("given they want to trade with me, what do they know?"). This links Day 1 to today.

**MIT 18.05 Class 3 (Bayes):** the tree and the table method. Learn the **table**: hypothesis | prior | likelihood | prior × likelihood | posterior. You'll use it for every strategy decision.

**MIT 18.05 Classes 4–5:** E[X+Y] = E[X] + E[Y] *always*; Var(X+Y) = Var X + Var Y *only if independent*. The second fact is the whole of diversification.

**Tversky & Kahneman 1971:** trained scientists expect small samples to look like the population. You will too. Count how often today.

**Ioannidis 2005:** when true effects are rare and many are tested, most "significant" findings are false. Replace "research finding" with "backtest" and reread the corollaries.

**Gigerenzer:** convert probabilities to counts ("out of 1,000 days...") and Bayes becomes easy. Do problem 3 this way.

**Miller & Sanjurjo 2018:** in short sequences, measuring "what happens after a streak" is biased even for a fair coin. Any backtest rule like "buy after 3 down days" is exposed to this.

**Lo 2002:** a Sharpe ratio is an estimate with a standard error. Table 1 tells you how wide the error is for a given sample length.

---

## Mentor's rules for Day 2
1. **Gut first, math second, always.** Log the gap. Shrinking that gap over 28 days is the real training.
2. **Say the base rate out loud** before judging any signal, record, or backtest.
3. **"Positive EV" isn't a plan.** Ask "what's the variance, and can I survive the bad path?" That's tomorrow's Kelly lesson.

Send me: your 10 answers (with gut guesses), your prediction sheet, and your answers to the lab's 4 questions.
