# Solutions. Open only after all 10.

1. Time-series: an asset's OWN past return predicts its future (go long if it rose). Cross-sectional: assets that beat their PEERS keep beating them (long winners, short losers). **Only time-series works with one ETF long/flat.** *Your realistic momentum family is a trend filter, not a stock-momentum portfolio.*

2. Trend: hedgers and slow updaters who trade against trends (MOP 2012: speculators profit at hedgers' expense). Mean reversion: impatient traders who demand liquidity and pay to exit now. Carry: those who need insurance or funding certainty. Event: forced/rule-based traders (index funds on rebalance day, month-end flows). Pairs: temporary liquidity shocks in one leg. *If you can't name your loser, you might be the loser.*

3. NIFTYBEES carry ≈ dividend yield minus the expense ratio (a percent or so). A liquid-fund ETF's carry ≈ the overnight/short-term rate. Real carry trades need futures curves, FX forwards, or borrowing: all banned here. *Our "carry" is the cash yield we earn while out of the market. Count it in every long/flat backtest.*

4. 10% × (1 − 0.58) ≈ **4.2%**, and 4.2% − 4% costs ≈ **0.2%**: nothing. *Assume published edges are half-dead before you start, and design for low cost.*

5. A full flip every week ≈ 4–5 full turns a month ≈ **400–500% monthly turnover**, far above 50%. *Weekly or faster rules need an edge measured in many bps per trade. You saw on Day 7 what that costs.*

6. Correlation is about daily moves together; cointegration is about the LEVELS staying tied. Banks can outperform the index for years (rate cycles, credit growth) while still moving with it daily. *Correlation is not mean reversion. Test the spread, not the returns.*

7. Big-return days cluster. Products z_t·z_{t−1} have fat-tailed, autocorrelated variance, so the naive SE (1/√n) is too small. Newey-West widens it. *Always use robust standard errors on daily financial data.*

8. The expected max of 8 |N(0,1)| ≈ 1.6–1.7, and |t| > 2.49 happens by luck in roughly 8% of 8-test batches. Suggestive at best; far below t > 3. *A clue for a card, not evidence.*

9. Once you've seen the out-of-sample period, every later choice is unconsciously shaped by it, and you can never get a clean test back. Not testing leaves the option open. *The locked sample is your most valuable and least renewable asset.*

10. (a) It's a long-short portfolio of individual stocks; our universe is index ETFs. (b) It needs shorting (banned: no F&O, no borrowing). (c) High turnover + 0.2% delivery STT on stocks. (d) Drawdowns of −53% break any rulebook. Honest route: an exchange-listed momentum-index ETF (long-only, e.g. one tracking the NIFTY200 Momentum 30 index), studied as a single instrument with its own costs and tracking. *Literature tells you where to look; the universe tells you what you can actually trade.*
