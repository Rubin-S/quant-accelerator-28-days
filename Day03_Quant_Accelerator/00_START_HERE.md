# DAY 3: Mon 2 Nov 2026
## Kelly sizing: how much to bet, and why too much ruins a winner

Day 1: who pays whom. Day 2: whether you're actually being paid, and how small samples lie.
Today: **given an edge, how big a bet?** This is where most people with a real edge still go broke.

Three ideas to own by tonight:
1. **Positive EV isn't enough.** You live one path through time, not the average of a crowd. Maximise *growth* (log wealth), not EV.
2. **Over-betting is far worse than under-betting.** Half Kelly keeps 75% of the growth; 2x Kelly has zero growth and certain deep drawdowns.
3. **You never know your edge.** Size for the pessimistic end of your estimate. In practice that means half Kelly or less, and a hard leverage cap.

**Deliverable (from the plan):** Kelly notebook with a ruin chart: run `kelly_lab` (folder 04) with predictions written first. Plus the 10 problems and your first draft sizing rule.

---

## Your day (about 6 h; deep work about 4 h)

| Time | Block | What | Files |
|---|---|---|---|
| 30 min | Drill | Zetamac 2×2 min + `make_a_market.py` from Day 2, 5 rounds. Log both. | |
| 45 min | Deep 1: The experiment | Haghani & Dewey (8 pp.). Before reading past page 2, write down how YOU would have bet. Then read how 61 finance-trained people did. | 02_kelly_in_practice/ |
| 75 min | Deep 2: The source | Thorp 2006: sections 1–4 (coin tossing, Kelly formulas, the long run) and section 7 up to eq. 7.11 (Kelly for stocks, chance of a drawdown). Skip blackjack and sports. Then MacLean, Thorp & Ziemba: just the lists of Good and Bad properties. | 01_, 02_ |
| 60 min | Deep 3: Lab | Fill `prediction-sheet.md`, then run `kelly_lab.py` (or the `.ipynb`). Answer its 4 questions. **This is the Day 3 deliverable.** | 04_build_along/ |
| 60 min | Deep 4: Problems + rule | 10 problems. Then fill `sizing-rule-draft.md`: your first written risk rule. | 05_, 06_ |
| 45–60 min | Light | Videos: *The Kelly Criterion* (Mutual Information), Ole Peters on multiplicative dynamics, Thorp interview. Optional: Kelly's own 1956 paper, pp. 917–920, just to see where it came from. | RESOURCES.md |
| 15 min | Review | Training log row, trial log (still empty) | |

---

## What to pull from each reading

**Haghani & Dewey (2016):** about 30% of quant-trained people went bust on a coin rigged 60/40 in their favour, and only 21% hit the cap. Note every bias they list. Which one would have got you?

**Thorp (2006), §2–4:** the Kelly fraction for coin tossing, why Kelly maximises long-run growth, and that over a short run Kelly can still lose to other strategies. §7: Kelly for stocks (f* = μ/σ²) and the formula for the chance of ever falling to x% of your wealth. Problem 8 uses it.

**MacLean, Thorp & Ziemba (2010):** the honest list. *Good:* fastest long-run growth, never bets you to zero. *Bad:* very volatile in the short run, and it can take a very long time to dominate. Fractional Kelly trades growth for safety.

**Peters & Gell-Mann (2016), optional:** why the expected value can rise while almost everyone loses. That's the +50%/−40% coin in problem 4. Read the introduction and the first example.

**Busseti, Ryu & Boyd (2016), optional/advanced:** Kelly with a hard limit on drawdown probability, solved as a convex optimisation, with code. Bookmark it for Week 3 when you size a real strategy.

---

## Mentor's rules for Day 3
1. **Size from the bottom of your edge estimate, never the middle.**
2. **Hard cap: 1.0x, no borrowing, for the whole 28 days.** Kelly may say more. Kelly doesn't know your μ is a guess.
3. **Write the sizing rule BEFORE you see a backtest.** A rule written after the backtest is just the backtest talking.

Send me: your lab predictions vs results, the 4 lab answers, the 10 problems (with gut guesses), and your sizing-rule draft.
