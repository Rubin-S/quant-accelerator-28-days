# 8-point paper checklist: one sheet per survivor
Score each point **0 = fail, 1 = shaky, 2 = solid**, and give the evidence in one line with a number. No 2019+ data.

| # | Check | Pass bar | Evidence (number + source) | Score |
|---|---|---|---|---|
| 1 | **Economic reason** | Named payer + mechanism + why it isn't arbitraged away | | |
| 2 | **Costs survive** | Expected edge per trade ≥ 2–3x round-trip cost (Day 7) **and** after 20.8% STCG tax | | |
| 3 | **Capacity** | Your order ≤ 1% of the ETF's median daily traded value; spread known | | |
| 4 | **Not hidden beta** | Factor regression (IIMA MF/SMB/HML/WML): know what's beta and what's left; call it alpha only if alpha t > 2 | | |
| 5 | **Enough bets** | A few hundred independent bets **OR** confirm mode: outside evidence t ≥ 3 + same sign in our data | | |
| 6 | **Bad regimes** | Story + numbers for 2008, 2011, 2013 taper, 2015–16 (exploration years). 2020 = story only (it's locked) | | |
| 7 | **Simple** | ≤ 3 parameters, all from the literature, not tuned | | |
| 8 | **Executable** | Signal known BEFORE the trade; price you assume is a price you can get (NSE close is a VWAP or CAS price) | | |

**Total /16:**   **Any zero?** (any 0 = fail, whatever the total)
**Overlay or alpha?** (be honest)
**Verdict:** PASS → Day 12 candidate / BACKUP / FAIL
**What would change my mind:**

## Mentor's note on point 5 (read before scoring)
The curriculum says "a few hundred independent bets". A monthly trend rule makes about 10–20 real decisions in
10 years, so it can **never** pass point 5 on our data alone. That's not a loophole; it's arithmetic. Such rules may
pass only in **confirm mode**: strong outside evidence (Hurst–Ooi–Pedersen: positive in every decade since 1880;
Moskowitz–Ooi–Pedersen 2012), plus the same sign here, plus a pre-registered single test. If you can't name that
outside evidence, score it 0.
