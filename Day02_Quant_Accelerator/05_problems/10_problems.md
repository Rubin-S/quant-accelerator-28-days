# Day 2: 10 problems (your deliverable)
Rules: pen and paper first. For each one write (a) your 10-second gut guess, (b) your worked answer, (c) one line on what it means for trading.
Then check with code if you like. Open SOLUTIONS only after all 10 are done. Grade: how far off was your gut?

1. **Reroll game.** Roll a fair die; you're paid its face value in rupees. After the first roll you may reroll once, and then you must take the second roll. What's the fair price of this game, and what's your rule for rerolling?

2. **A small edge, 100 times.** Each trade wins Rs 200 with probability 0.55 or loses Rs 200 with probability 0.45. You make 100 independent trades. Find the expected total, the standard deviation of the total, and the probability you finish with a loss. Use both a normal approximation and the exact binomial.

3. **Signal or noise (Bayes).** 10% of days are "big up" days. Your indicator fires on 80% of big-up days and on 20% of all other days. It fires today. What's the probability today is a big-up day?

4. **Is my backtest real? (Ioannidis-style)** Say 1 in 20 strategy ideas you test has a real edge. A real edge passes your backtest 50% of the time; a fake one passes 5% of the time (p < 0.05). A strategy passes. What's the probability it's real? What happens if 1 in 100 ideas is real?

5. **Martingale.** Bet Rs 100 on red in European roulette (P(win) = 18/37). After a loss, double the bet. You stop after a win, or after 6 straight losses (Rs 6,300 lost). What's the EV of one cycle? What's the probability of the 6-loss disaster? Why does the strategy *feel* safe?

6. **The star fund manager.** 1,000 managers have zero skill, and each beats the market in a given year with probability 0.5. How many do you expect to beat it in at least 7 of 10 years?

7. **Waiting for patterns.** On average, how many fair-coin flips until you see HH? How many until you see HT? Why are they different when both have probability 1/4 on any given pair?

8. **Mean vs median (preview of Day 3).** A stock starts at Rs 100. Each day it goes up 1% or down 1% with equal probability. After 250 days, what's its expected price? What's its median price? (Assume 125 ups and 125 downs for the median.) Why do they differ?

9. **Linearity and diversification.** You hold 10 stocks. Each goes up tomorrow with probability 0.6. (a) Expected number going up? (b) Variance of that number if they're independent? (c) Variance if they're perfectly correlated (all up or all down together)? What does this say about "diversified" portfolios of correlated stocks?

10. **Make the trade?** Someone offers to sell you the maximum of two fair dice rolls, paid in rupees, for Rs 4.25. Do you buy? What's your edge per trade? At what price would you sell it?
