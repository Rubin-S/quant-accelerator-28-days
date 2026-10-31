# Day 28 resources: graduation and go/no-go (checked 1 Nov 2026)

All free. Most of what you need was already built in Days 1–27; today's reading is about **launching safely**.

## Read today
1. **Google SRE Book ch. 27, "Reliable Product Launches at Scale"** (Singh, Kirsch, Rau), 30 min. Read "The Launch Checklist" (every question must be backed, ideally, by a past launch disaster), "Gradual and Staged Rollouts" (canaries), and "Rollout Planning" (contingency measures). Your ramp plan is a canary. https://sre.google/sre-book/reliable-product-launches/
2. **Google SRE Book Appendix E, "Launch Coordination Checklist"**, 10 min. Skim it, then cut it down to your own one-page first-live-day checklist (04_templates). https://sre.google/sre-book/launch-checklist/
3. **Zerodha Varsity, Module 9 "Risk Management & Trading Psychology"** (Karthik Rangappa, free), 40 min, chapters on position sizing and your trading psychology. Written for Indian retail traders, on your broker. https://zerodha.com/varsity/module/risk-management/

## Re-read from earlier kits (not repeated here)
- **Bailey & López de Prado (2012), "The Sharpe Ratio Efficient Frontier"**: Minimum Track Record Length (Day 5 kit). gonogo.py uses its formula to tell you how many years live P&L stays noise.
- **Klein's pre-mortem** (Day 10 kit): section 3 of your memo.
- **SEBI retail algo framework** (4 Feb 2025 circular, live 1 Apr 2026; Day 21 kit): static IP, 2FA, under 10 orders a second needs no registration.
- **Knight Capital SEC order** (Day 21): why a wrong live deploy is the most expensive mistake in this whole course.
- Kite exceptions (Day 27), Zerodha kill switch (Day 24), parity (Day 23), holdout seal (Day 20), rulebook lock (Day 21).

## Build-along (03_build_along): 59 tests pass, plus Day 27's 2 xfails until you fix them
- `gonogo.py`: reads your evidence pack and checks seven gates. **G0** the strategy passed its own pre-registered holdout test; **G1** no unexplained orders; **G2** signal parity; **G3** slippage; **G4** failure drills (12 of 12 plus the game day); **G5** integrity (rulebook hash, holdout opened once); **G6** human (money you can lose, written memo). It also computes the minimum track record length. It can say NO-GO by itself; GO only ever means **Stage 1**.
- `demo_gonogo.py`: a full evidence pack from the demo paper weeks gives **NO-GO**, on purpose: G4 fails (the Day 27 bug is still in this code) and G6 fails (stub memo). Checked: with the Day 27 fixes and a real memo, it gives GO: STAGE 1 ONLY.
