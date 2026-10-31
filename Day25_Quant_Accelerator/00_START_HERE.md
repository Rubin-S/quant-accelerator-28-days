# DAY 25: Tue 24 Nov 2026 (NSE closed, Guru Nanak Jayanti): REVIEW, FIX, SEE
## Read session 1 like an auditor. Fix with tests. Build the page you'll check every day.

| Time | Block | What | Files |
|---|---|---|---|
| 20 min | Drill | Read 3 journal days → write each session's contract result by hand before running the tool | |
| 30 min | Read | SRE postmortem chapter + Allspaw "Blameless PostMortems" | RESOURCES |
| 20 min | Demo | `python demo_week.py` → open `demo_out/dashboard.html` + `review.md` | 03_ |
| 30 min | Review | `python session_review.py --bars … ` on YOUR session-1 files | 03_ |
| 45 min | Fix | each anomaly → bugs.md: failing-first test → fix → full suite → replay parity still 0 | 04_ |
| 25 min | Build | `python dashboard.py …` on the VM; view through the SSH tunnel | 03_ |
| 20 min | Write | 1-page postmortem of session 1 | 04_ |
| 20 min | Problems | 10 problems | 05_ |
≈ 3.5 h.

## The 8 session contracts (session_review.py)
C1 one EOD line a day · C2 no crash · C3 every order resolved · C4 a blocked order is never sent · C5 no unexplained mismatch · C6 book = broker · C7 every CRIT has an incident note · C8 orders only after a decision or a labelled drill.
A breach becomes a documented event only when incidents.md has a dated note with a cause and a fix.

## Demo week (9 sessions with 3 planted events)
Forced drill → 1 paper buy, shortfall −9.2 bps (noise) · missing preflight → abort + CRIT · planted +5 units → mismatch HALT + CRIT → note → cleared. Contract breaches after the notes: **0**.

## Mentor's rulings
1. **No fix without a failing-first test**, and replay parity must stay at 0 (Days 16 and 23 rules).
2. **If a "fix" changes when or what you trade, it's a rule change.** 48-hour cooling-off, trial log, no exceptions in Week 4.
3. **The dashboard shows; it never acts.** Actions go through kill.py and the runbook.
4. **Postmortems are blameless and specific.** "Be more careful" is not an action item.
5. Paper equity vs buy & hold after a week is noise. Don't read it, don't react to it.

Send me: review.md + bugs.md (with red→green test output) + postmortem.md + a dashboard screenshot + `pytest -q` (31) + 10 problems + training-log row.
Day 26 (Wed 25 Nov): paper session 2 + live-vs-backtest diff (signals, fills, slippage).
