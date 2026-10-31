# Day 3 resources: Kelly, fractional Kelly, ergodicity, ruin
All free. ✅ = PDF already in this ZIP. Links checked 31 Oct 2026.

## 1. The originals (folder 01)
- ✅ Kelly (1956), "A New Interpretation of Information Rate", Bell System Technical Journal: where it started (as information theory, not finance).
- ✅ Thorp (2006), "The Kelly Criterion in Blackjack, Sports Betting, and the Stock Market", Handbook of Asset and Liability Management. **The core reading for today.**
- Breiman (1961), "Optimal Gambling Systems for Favorable Games": the proof that Kelly maximises long-run growth. Reference list (no reliable free PDF I could verify): http://stat.wharton.upenn.edu/~steele/Resources/FTSResources/KellyBreiman.htm

## 2. Kelly in practice (folder 02)
- ✅ Haghani & Dewey (2016), "Rational Decision-Making Under Uncertainty: Observed Betting Patterns on a Biased Coin". Elm Wealth's own write-up: https://elmwealth.com/lessons-from-betting-on-a-biased-coin-cool-heads-and-cautionary-tales
- ✅ MacLean, Thorp & Ziemba (2010), "Good and Bad Properties of the Kelly Criterion"
- ✅ Busseti, Ryu & Boyd (2016), "Risk-Constrained Kelly Gambling" (Stanford). Code: https://github.com/cvxgrp/kelly_code

## 3. Ergodicity and ruin (folder 03)
- ✅ Peters & Gell-Mann (2016), "Evaluating Gambles Using Dynamics", Chaos (arXiv version)
- Peters (2019), "The Ergodicity Problem in Economics", Nature Physics: https://www.nature.com/articles/s41567-019-0732-0
- Ergodicity Economics site (lecture notes, interactive coin-toss apps): https://ergodicityeconomics.com/

## 4. YouTube
1. Mutual Information, *The Kelly Criterion*: the biased-coin game, growth rates, and why Kelly is dangerous. Best single explainer. https://www.youtube.com/watch?v=-9JM9suCIHs
2. Ole Peters, *Random multiplicative dynamics* (Ergodicity TV): why the average and the typical path split apart. https://www.youtube.com/watch?v=CCLtQHL-VUs
3. *Gambling With an Edge*, guest Ed Thorp: the man who first used Kelly for real money, in his own words. https://www.youtube.com/watch?v=D5FLKOmfdTM
4. Nassim Taleb, *How you will go bust on a favorable bet (Kelly/Shannon/Thorp)*. https://www.youtube.com/watch?v=91IOwS0gf3g
5. *Edward Thorp on gaining an edge in the market and in life*: a longer talk, for the light block. https://www.youtube.com/watch?v=HsspiVJM_rs
6. Already in your Day 1 list: Paolucci, *Why Most Traders Lose: Ergodicity for Quant Trading*. https://www.youtube.com/watch?v=dryV1qJYUw8

## 5. Blogs (practitioner view)
- Rob Carver, *If you're so smart, how come you're not SBF? The Kelly criterion and choice of expectations and utility function*: why he sizes from a pessimistic quantile, not the mean. https://qoppac.blogspot.com/2022/11/if-youre-so-smart-how-come-youre-not.html
- Rob Carver, *Kelly versus classical portfolio theory*. https://qoppac.blogspot.com/2018/06/kelly-versus-classical-portfolio-theory.html
- Rob Carver, *How much risk should we take?* (vol target = Sharpe, then cut it). https://qoppac.blogspot.com/2020/03/how-much-risk-should-we-take.html

## 6. GitHub
- cvxgrp/kelly_code: Boyd group's risk-constrained Kelly code (Python, CVXPY). Read after the lab. https://github.com/cvxgrp/kelly_code
- Your repo **probability-and-markets**: commit `kelly_lab.py` and your problems.

## 7. In this ZIP, built for you (folder 04)
- `kelly_lab.py` / `kelly_lab.ipynb`: 4 parts, all tested. Reference chart `kelly_lab.png`.
  - Growth curve
  - 10,000-player replay of the biased-coin game at ½x, 1x, 2x and 3x Kelly
  - Estimation error
  - Kelly leverage on an index

## 8. Books for later
- Edward Thorp, *A Man for All Markets* (autobiography: blackjack to hedge funds).
- William Poundstone, *Fortune's Formula* (the story of Kelly, Shannon and Thorp).
- Victor Haghani & James White, *The Missing Billionaires* (2023): sizing for real investors, from the coin-experiment author.
- MacLean, Thorp & Ziemba (eds.), *The Kelly Capital Growth Investment Criterion* (the full research collection).
