# Arnott–Harvey–Markowitz (2019) 7-category research protocol: our short version
Score each survivor 0/1 per line. Day 11's 8-point checklist builds on this.

**1 Research motivation**
- [ ] Economic story written BEFORE looking at results (payer, mechanism)
- [ ] Hypothesis is falsifiable

**2 Multiple testing**
- [ ] Every trial is logged (trial-log.md), including failures
- [ ] Hurdle raised for the number of trials (t > 3; deflated Sharpe on Day 20)

**3 Data and sample**
- [ ] Data choice justified before testing; survivorship-safe (index/ETF)
- [ ] Data cleaned with documented rules (bad ticks list), no tweaking to improve results
- [ ] Out-of-sample (2019+) untouched until the pre-registered test

**4 Cross-validation**
- [ ] OOS used once; walk-forward planned, not repeated until it works

**5 Model dynamics**
- [ ] Considered decay, crowding and regime change; rule for retiring the strategy

**6 Complexity**
- [ ] ≤ 3 parameters; chosen from literature, not optimised
- [ ] Can explain every rule to a 15-year-old

**7 Research culture**
- [ ] Failures reported to the mentor honestly; no reward for "finding" something
