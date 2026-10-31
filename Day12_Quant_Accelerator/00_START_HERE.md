# DAY 12: Wed 11 Nov 2026: PICK ONE, PICK A BACKUP, PRE-REGISTER, LOCK
## After today, the plan can't move. That's the point.

From Day 11 you have scored survivors. Today you commit, in writing, to exactly what you'll test, what result kills it,
and when. Then you hash it and push it to GitHub. On Day 20 you open the 2019+ holdout once and live with the answer.

| Time | Block | What | Files |
|---|---|---|---|
| 20 min | Drill | Zetamac + "true SR 0.6, 7.8 yrs: E[t]?" × 5 | |
| 35 min | Read | Nosek et al., *The Preregistration Revolution* (all 15 pages; focus on "postdiction vs prediction" and the section on pre-registering with data you've already seen) | 01_ |
| 35 min | Read | Harvey, *The Scientific Outlook in Financial Economics*: the intro, the p-hacking section and the closing guidelines | 01_ |
| 15 min | Re-read | Harvey–Liu–Zhu (t > 3) and Harvey–Liu *Backtesting* (haircuts), both already in your **Day 5** kit | Day 5 kit |
| 15 min | Watch | Brunel, "Why you should pre-register" (skim the walk-through) | |
| 40 min | Run | `python prereg_designer.py`: power table, fixed grid, bootstrap falsifier sizing. Predict first | 04_build_along/ |
| 75 min | Write | `preregistration-template.md`: every section, including backup + falsifier | 05_templates/ |
| 10 min | Lock | `python prereg_designer.py lock my_prereg.md` → git commit, tag `prereg-v1`, push | |
| 20 min | Problems | 10 problems | 06_problems/ |
≈ 4.4 h.

## What the designer shows (exploration data only)
- **Power:** a true Sharpe of 0.5 over a 7.8-year holdout clears t > 3 only **5%** of the time. t > 3 is the right bar
  for an ALPHA claim, and almost impossible to meet here.
- **Fixed grid (8/10/12m SMA):** Sharpe +0.25 / +0.21 / +0.14 vs buy & hold +0.27. The filter **doesn't** win on Sharpe.
- **Bootstrap (2,000 holdout-length samples):** vol ratio 0.65–0.87 (10th–90th pct), drawdown shallower than buy & hold
  84% of the time, CAGR give-up −8.1% to +0.5%, and P(return t > 3) ≈ 0%.
- **So:** for Faber, the testable hypothesis is about risk (vol ratio, drawdown, capped return give-up), not alpha.

## Mentor's rulings for today
1. **The t > 3 bar stands for any alpha claim.** For an overlay, the pre-reg replaces it with numeric risk falsifiers
   sized by the bootstrap, and states plainly that no alpha is claimed. That's a design decision, not a loophole. Write it down.
2. **Holdout boundary = 2019-01-01, written as a date.** This replaces the Day 17 "70/30" line in the plan
   (the 2019+ lock came first, on Day 8).
3. **Parameter chosen before the grid:** 10m (Faber 2007). Max 3 values × max 2 knobs, and all of them count as trials.
4. **Backup gets its own falsifier.** No backup = no Gate 2.
5. **Leakage note is mandatory.** Write what you already know about 2019–2026 markets.
6. **After locking:** any change = v2 file + reason + trial count up. Never edit v1.

Send me: the locked pre-reg + LOCK.txt + the GitHub tag link, the designer output, the 10 problems, and your trial-log
and training-log rows. Day 13 (Thu 12 Nov): data pipeline.
