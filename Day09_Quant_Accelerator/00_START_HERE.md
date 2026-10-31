# DAY 9: Sun 8 Nov 2026 (Diwali): LIGHT DAY
## Read two things well. Write 3 more idea cards. Then go celebrate.

Plan from the schedule: **read Chan ch. 1–2 + one SSRN paper → 3 more idea cards (6 total).** About 3 hours, no more.
Rest is part of training (Ericsson: deliberate practice needs recovery). The market's Muhurat session is at 14:20–15:30. We don't trade it.

| Time | Block | What | Files |
|---|---|---|---|
| 15 min | Drill | Zetamac only (light) | |
| 40 min | Read 1 | Chan ch. 1 (free publisher excerpt) + ch. 2 if you can get it legally (see the guide; if not, work from its table of contents) | 01_chan/ |
| 10 min | Method | Keshav, "How to Read a Paper" (2 pages): the 3-pass method | 03_how_to_read/ |
| 50 min | Read 2 | **The SSRN paper: Faber, "A Quantitative Approach to Tactical Asset Allocation"** (2013 update, 70 pp; read pp. 1–20 + the FAQ). Fill the paper-reading card. Original 2006 version included for comparison. | 02_ssrn_paper/, 06_templates/ |
| 25 min | Replicate | Predict first, then run `replicate_faber.py`: Faber's 10-month rule on NIFTY (and 50/50 with gold), 2008–2018 only, with Day 7 costs. +2 trials. | 05_build_along/ |
| 45 min | Cards | 3 new idea cards (6 total). Use Chan's "suits you" filter + his 7 pitfall questions. | 06_templates/ |
| 15 min | Problems | 10 short problems | 07_problems/ |

## Why Faber's paper?
It fits our rules almost exactly: one asset class at a time, long or cash, monthly, one parameter, famous enough
to be heavily criticised. That makes it perfect practice for reading a paper like a sceptic.

## What the replication found (2008-07 to 2018-12, exploration only)
| | CAGR | Vol | Max DD |
|---|---|---|---|
| NIFTY buy & hold (price index, no dividends) | 9.88% | 20.8% | −36.8% |
| NIFTY 10-month filter, net of costs | 8.87% | 14.8% | −19.4% |
| 50/50 NIFTY+gold, hold | 8.76% | 9.6% | −10.9% |
| 50/50, each filtered, net | 6.87% | 8.4% | −10.5% |
Faber's claim ("similar return, much lower drawdown") roughly holds on NIFTY. But the window starts in a crash, cash
is an assumed 6%, and on a diversified mix the filter only cost return. 21 switches cost about 0.14% a year in fees;
the real hidden cost is short-term tax. Questions 3–6 in the script make you face all of that.

## Mentor's rules for Day 9
1. **Read with a pencil:** every paper gets a reading card. No card, it didn't happen.
2. **Replicate before you believe:** small, honest, exploration window only.
3. **Legal sources only.**
4. **Rest is training.** Happy Diwali.

Send me (by Monday): 3 new idea cards, the Faber reading card, replication predictions vs actuals + 6 answers, the 10 problems.
