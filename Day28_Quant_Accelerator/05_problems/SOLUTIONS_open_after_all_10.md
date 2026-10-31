# Solutions
1. Evidence can prove a failure; it can't prove readiness: some things (your judgement, the money, the memo) only a human can sign. And any GO starts at Stage 1. *Machines veto; humans commit, small.*
2. NO-GO on the strategy. The system can run perfectly and still lose money on a rule that failed its own pre-registered test. Go back to Day 8–12 with a new idea; the plumbing is reusable. *Plumbing is not edge.*
3. "Slippage: assumed 5 bps per side; measured on n = __ fills, which cannot decide; treated as unverified; Stage 1 size is small enough that slippage 3× the assumption costs under ₹__ a year." *Say what you don't know, and cap what it can cost.*
4. Operations: zero unexplained orders, book = broker, alerts working, D1/D2 parity, slippage per fill, your own rule adherence. Not returns. *Judge what the sample can show.*
5. Nothing. Log it; it's noise (MinTRL); no size increase before the calendar and the evidence say so. *A win is not evidence.*
6. Nothing, if it's inside the predicted band and rules were followed; check that the stop numbers in memo section 2 aren't hit. *A planned loss is not a reason to change the plan.*
7. P&L over months is noise for this strategy; promoting on it means sizing up after luck and cutting after bad luck, the classic way to lose. *Size by process, not by mood.*
8. (a) Knight Capital: tested code, wrong deploy, $460m in 45 minutes (Day 21). (b) Day 27: tested code still had a "safe by accident" bug only a drill found. Live is a new environment; a canary is cheap insurance. *Tested ≠ proven in production.*
9. The broker can't lose money you didn't deposit; with Stage 1 funds only, even a runaway bug is capped. *Limit the blast radius physically, not just in code.*
10. Fix BUG-27-1 (and 27-2) with failing-first tests so drills reach 12/12 (G4), and write ≥ 300 honest words of memo sections (G6). Editing evidence to flip a gate is falsifying your own record: the same sin as peeking at the holdout. *Change reality, not the report.*
