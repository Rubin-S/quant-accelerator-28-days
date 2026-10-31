# Solutions. Don't open until all 10 are attempted.

1. f* = 0.55 − 0.45 = **10%**. g = 0.55·ln(1.1) + 0.45·ln(0.9) = **+0.0050 per bet** (about 0.5%). Small edge, small bet, slow growth. That's normal. *Trading: a real 55% edge compounds slowly. Anyone promising fast growth from a small edge is over-betting.*

2. f* = (2·0.40 − 0.60)/2 = **10%**. g = 0.40·ln(1.2) + 0.60·ln(0.9) = **+0.0097 per bet**, about double #1. A 40% win rate can beat a 55% one. *Win rate means nothing without the payoff. Never judge a strategy by its hit rate.*

3. f* = 0.45 − 0.55 = −0.10, so you **bet zero** (you're not allowed to take the other side here). The gut trader bets MORE after losses ("it's due"). That's the gambler's fallacy from Day 2, plus a bigger stake on a negative-EV bet: the fastest route to ruin.

4. EV per flip = 0.5(1.5) + 0.5(0.6) = **1.05, so +5%**. But one person's growth per flip = √(1.5 × 0.6) = **0.949, so −5.1%**. After 100 flips: the **average** is 1.05^100 ≈ **131x**, but the **median** is 0.9^50 ≈ **0.005x** (you've lost 99.5%). The average is carried by a tiny number of astronomically lucky people. *You live one path through time, not the average across a crowd. This is ergodicity, and it's why Kelly maximises log wealth.*

5. **11.1%, 25%, 100%, 900%.** Recovery needed = 1/(1 − loss) − 1. Losses hurt more than equal gains help, and that asymmetry grows with size. *That gap is exactly the −f²/2 term in the growth formula. Big bets pay it squared.*

6. Sharpe = 8/20 = **0.40**. L* = 0.08/0.04 = **2.0x**. Growth: 1x → **6.0%**, 2x → **8.0%** (the max, = SR²/2), 3x → **6.0%**, 4x → **0%**. Note that 1x is half Kelly here and keeps 75% of the max growth with half the volatility. *If the true μ is 4%, not 8%, then 2x leverage earns 0% and 4x loses badly. Your μ estimate is the weak link.*

7. SE = √(0.58 × 0.42 / 100) = **0.049**. 95% range ≈ 0.58 ± 0.10, so **0.48 to 0.68**. At 0.48 an even-money bet has negative edge, so Kelly says **bet zero**. *100 trades can't distinguish a good strategy from a losing one. Size for the bottom of your range, not the middle.*

8. Full (c=1): 0.5^1 = **50%**. Half (c=0.5): 0.5^3 = **12.5%**. Quarter (c=0.25): 0.5^7 = **0.8%**. 2x (c=2): 0.5^0 = **100%**, so it's certain. *Half Kelly gives up 25% of growth to cut the chance of halving from 1 in 2 to 1 in 8. That's why pros live at half Kelly or below.* (Thorp 2006, section 7. Continuous-time result, approximate for discrete bets.)

9. **No.** With the cap, the upside is limited but the downside isn't, so the payoff is no longer "log wealth forever". Bet much less, or just enough to reach $250, and protect what you have. Haghani & Dewey report that a constant 10–20% bet should have got about 95% of players to the cap; only 21% got there, and about 30% went bust. *Kelly assumes you play forever with no ceiling. Change the objective (a cap, a deadline, needing the money next month) and the right bet size changes. Write your real objective down first.*

10. (a) t ≈ SR × √years = 0.8 × √10 = **2.5**. That's below our t > 3 bar, so this strategy wouldn't even pass. (b) Haircut SR = 0.4. Full Kelly targets **40%** annual vol (vol target = Sharpe); half Kelly targets **20%**. (c) Half Kelly wants 20%/16% = 1.25x the ETF, but the rule caps it at **1.0x, so Rs 1,00,000 in the ETF at most** (and less while you're in paper trading). *Write this sizing rule in your rulebook now, before a backtest can tempt you.*
