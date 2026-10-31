# Day 3: 10 Kelly problems
Rules as before: gut guess → worked answer → one line on what it means for your trading. Solutions only after all 10.
Formulas you need: even money f* = p − q. Odds b:1 → f* = (b·p − q)/b. Growth per bet g(f) = p·ln(1+b·f) + q·ln(1−f).
Continuous (stocks): Kelly leverage L* = μ/σ², growth g(L) = L·μ − L²σ²/2 (excess over cash).

1. **Thin edge.** Even-money bet, p = 0.55. What's the Kelly fraction? What's the growth per bet at Kelly?

2. **Long shot.** A bet pays 2:1 (win Rs 2 per Rs 1 staked, or lose the Rs 1). p = 0.40. Kelly fraction? Is this bet better or worse than #1 for growth?

3. **No edge.** Even money, p = 0.45. What does Kelly tell you to bet? What does a "gut" trader usually do after five losses in a row here?

4. **Peters' coin (ergodicity).** Each flip, your wealth rises 50% on heads or falls 40% on tails. EV per flip? Growth per flip for ONE person who plays forever? After 100 flips, what's the typical (median) outcome vs the average outcome?

5. **Drawdown arithmetic.** What gain do you need to recover from losses of 10%, 20%, 50%, 90%? Why does this make big bets worse than they look?

6. **Kelly on an index.** Assume an index has excess return μ = 8% and volatility σ = 20% (an assumption, not a forecast). Find the Sharpe ratio, the Kelly leverage, and the growth rate at 1x, 2x, 3x and 4x leverage.

7. **How sure is your edge?** Your 100 backtest trades won 58% of the time. What's the standard error of that win rate? What's a 95% range? What does Kelly say at the bottom of that range?

8. **Odds of halving (Thorp 2006, eq. 7.11).** For fractional Kelly c (c = 1 is full Kelly), the chance your wealth EVER falls to a fraction x of where it started is x^(2/c − 1). Find the chance of ever losing half your money at full, half, quarter and 2x Kelly.

9. **The capped game.** In the Haghani-Dewey game the payout was capped at $250 (players weren't told the cap until they got close). You're at $240 with plenty of time left. Should you keep betting 20%? What changes?

10. **Size your future strategy (write the rule before you have a backtest).** Rs 1,00,000 account. Your future strategy shows a backtest Sharpe of 0.8 on 10 years of data. (a) What's its t-stat? (b) Cut the Sharpe in half for overfitting and costs (a common haircut). What annual volatility does full Kelly target? What does half Kelly target? (c) A NIFTY ETF has about 16% annual vol (we'll measure it on Day 4). How much of the account goes into the ETF if your rule also says "never more than 1x, no borrowing"?
