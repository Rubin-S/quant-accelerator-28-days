# DAY 10: Mon 9 Nov 2026: THE KILL SESSION
## I attack your cards. You defend. About 3 of 10 survive.

**Deliverable:** 4 more idea cards (10 in total), then all 10 through the card killer and the kill session. Survivors
get a pre-mortem. Tomorrow (Day 11, market shut) the survivors face the 8-point paper checklist.

A trader's real skill isn't finding ideas. It's killing them cheaply, before they cost money. At a desk, the
juniors who lasted were the ones who could hear "that's dead" without arguing with the data.

| Time | Block | What | Files |
|---|---|---|---|
| 20 min | Drill | Zetamac + 2 mental cost checks: "edge X bps, cost 13.9 bps, alive?" | |
| 45 min | Read | **Hou–Xue–Zhang** intro + Table 1 (most anomalies don't replicate) → **Jensen–Kelly–Pedersen** abstract + intro (the other side) → **Novy-Marx–Velikov** abstract + intro (costs kill high turnover) | 01_, 02_ |
| 20 min | Read | **Arnott–Harvey–Markowitz** backtesting protocol (11 pages, all of it) | 03_kill_methods/ |
| 10 min | Watch | Kahneman on the pre-mortem (3 min) + Harvey on the risks of historical backtests | RESOURCES.md |
| 45 min | Write | 4 new idea cards → 10 in total | Day 8 idea-card template |
| 30 min | Run | Enter all 10 into `my_cards.csv` → `python card_killer.py my_cards.csv`. Predict each verdict FIRST. | 04_build_along/ |
| 60 min | Kill session | For each card: the 12 attacks, a defence sheet, then accept the verdict | 05_templates/kill-session-protocol.md |
| 20 min | Pre-mortem | One per survivor | 05_templates/premortem-template.md |
| 20 min | Problems | 10 problems | 06_problems/ |
≈ 4.5 h. That's the deep-work ceiling; stop there.

## The card killer on my 10 demo cards (numbers are my rough priors from Day 8, not facts)
| Card | Verdict | Why |
|---|---|---|
| Overnight NIFTYBEES | KILL | 9.1 bps gross < 13.9 bps cost: −25% a year (t 2.49 meant nothing) |
| Turn-of-month | PARK | net 8 bps per trade, thinner than 2x cost |
| Faber 10-month filter | SURVIVE (overlay) | costs about 0.28% a year; a drawdown tool, not alpha |
| 12-month trend | SURVIVE (confirm mode) | a century of outside evidence; discovering it alone would need about 1,600 years |
| 1-month trend | KILL | our data says the wrong sign |
| BANK/NIFTY pairs | KILL | needs shorting |
| Intraday mean reversion | KILL | costs eat it |
| High-VIX buying | PARK | needs about 95 years to prove |
| NIFTY vs gold rotation | KILL | wrong sign |
| Nifty200 Momentum 30 ETF | SURVIVE (confirm mode) | IIMA momentum t ≈ 3.1; ETF is long-only, check liquidity |
5 killed, 2 parked, 3 survived. That's the shape of a real research pipeline.

## Mentor's rules for Day 10
1. **Predict the verdict before running the script.** Where you were wrong is where you learn.
2. **No 2019+ data in defences.** Ever.
3. **Accept the kill gracefully.** Arguing with a dead card is how traders blow up.
4. **Parked isn't dead:** write exactly what would un-park it.
5. **The script is a filter, not a judge.** I'll still attack your survivors' payer stories.

Send me: 10 cards, `my_cards.csv` + verdicts, 10 defence sheets, survivor pre-mortems, the 10 problems, and trial-log/training-log updates.
