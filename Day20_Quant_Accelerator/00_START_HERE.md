# DAY 20: Thu 19 Nov 2026: THE ONE LOOK
## Open 2019–2026 once. Grade the rule and grade yourself.

**Order matters. Do it in this sequence. Don't open anything sealed early.**

| Step | Time | What | Files |
|---|---|---|---|
| 1 | 20 min | Drill: "SE of an 8-year Sharpe?" "E[max of 25 zero-skill Sharpes]?" × 5 | |
| 2 | 60 min | Read the base rates: Falck et al. (intro, section 3), McLean-Pontiff (abstract, OOS section), Hurst et al. (skim exhibits) | 01_ |
| 3 | 20 min | Problems 1–5 (before sealing) | 05_ |
| 4 | 40 min | Fill `04_templates/predictions.json`: point + 90% interval for 6 numbers, 3 probabilities, your locked falsifier lines, your Day 17 DSR N and trial-Sharpe std, reasoning | 04_ |
| 5 | 5 min | `python seal_predictions.py --prereg <yours> --lock <LOCK.txt> --pred ../04_templates/predictions.json`, which prints the password | 03_ |
| 6 | 10 min | Unzip `06_data/SEALED_holdout_2019_2026.zip`. Build or extend your NIFTYBEES 2019–2026 series (bhavcopy, split ex 2019-12-19) | 06_ |
| 7 | 15 min | `python holdout_report.py --pred ../04_templates/predictions.json --full-signal <FULL csv> --cash <cash 2007_2026 csv> --trade <your NIFTYBEES>`, **once** | 03_ |
| 8 | 45 min | `holdout-writeup.md` + problems 6–10 | 04_, 05_ |
| 9 | after | Open my sealed demo report and compare. Mine ran on the index stand-in. | demo/ |
≈ 3.8 h.

## Mentor's rulings for today
1. **Predictions first, data second.** The scripts enforce it, the log records it, and I grade the log.
2. **One run.** `OPENED.log` counts runs. A second run gives the same numbers by construction. Anything you change before a second run makes it a new strategy, with no clean data left to test it on.
3. **The verdict is the pre-registered falsifiers, as written.** No "adjusting for COVID", no re-cut dates, no new lookbacks.
4. **The real verdict runs on NIFTYBEES** (`--trade`). The index run is a cross-check only.
5. Surviving ≠ proven. A surviving claim goes into the Day 21 rulebook as "not yet refuted", with this report attached.
6. Write your DSR N exactly as decided on Day 17. If you change it now, say so and why.

Send me: HOLDOUT_REPORT.md + OPENED.log + PREDICTIONS_LOCK.txt + predictions.json + write-up + problems + training-log row.
Day 21 (Fri 20 Nov, Gate 3): signed rulebook: sizing, risk limits, kill switches, what you'll trade and when.
