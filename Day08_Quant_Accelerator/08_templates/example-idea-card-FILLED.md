# EXAMPLE CARD (worked by your mentor: copy the depth, not the idea)

**Name:** Slow trend filter on NIFTYBEES   **Family:** trend (time-series momentum)   **Looked at 2019+?** NO

1. **Bet:** "When NIFTY's 12-month return is positive, holding NIFTYBEES over the next month beats holding cash
   on a risk-adjusted basis, because trends persist for months and then partially reverse."
2. **Why it pays:** Behavioural + structural: slow information diffusion and herding (Moskowitz-Ooi-Pedersen 2012);
   speculators profit at hedgers' expense. Main pain: sharp V-shaped reversals (2020).
3. **Rule:** Month-end: if 12-month log return of NIFTY > 0, hold NIFTYBEES next month; else hold a liquid/overnight
   fund ETF. One parameter (12 months), the paper's default. About 2–4 round trips a year.
4. **Costs:** About 3.9 bps per round trip at ₹1 lakh + 5 bps spread assumption → under 0.05% a year. Tax: each exit
   with a gain held < 12 months pays 20.8%. That's the real cost.
5. **Expected edge:** The paper's evidence is a diversified long/SHORT futures portfolio. A single-index long/flat
   version mainly cuts drawdowns; it usually LOWERS return vs buy-and-hold. Honest goal: similar return, smaller
   drawdowns. After a haircut: maybe no excess return at all.
6. **Evidence (2007–2018):** Explorer T1 (long/short version): t = 0.8. Weak. One test among 8.
7. **Dies if:** out-of-sample max drawdown is not at least 25% smaller than buy-and-hold, or Sharpe is below
   buy-and-hold minus 0.1. Should lose in choppy, trendless years (2011–2013 type).
8. **Score:** payer 4 / fits 5 / costs 4 / literature 4 / testable 5 / params 5 = 27. Survives to Day 11. Expect it to die there.
