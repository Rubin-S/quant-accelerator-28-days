# Solutions. Don't open until all 10 are attempted.

1. **Rs 4.25.** Reroll if the first roll is 1, 2 or 3 (each is below the 3.5 average of a fresh roll). EV = (4+5+6)/6 + (3/6)(3.5) = 2.5 + 1.75 = 4.25. *Trading: decide your rule by comparing against the EV of the alternative, not by how a number "feels".*

2. Per trade: EV = 0.55(200) + 0.45(-200) = **+Rs 20**. Var = 200^2 - 20^2 = 39,600, SD = 199. Over 100 trades: **EV = +Rs 2,000, SD = Rs 1,990**. P(loss): normal ~ Phi(-2000/1990) = **15.7%**. Exact: a loss means 49 or fewer wins out of 100 with p = 0.55, which is **13.5%**. *Trading: even a 55% edge loses money over 100 trades about 1 time in 7. A losing streak is not proof the edge died.*

3. P(up | fire) = (0.10 x 0.80) / (0.10 x 0.80 + 0.90 x 0.20) = 0.08 / 0.26 = **30.8%**. *Trading: an "80% accurate" signal is right less than a third of the time here, because big-up days are rare. Always ask for the base rate.*

4. P(real | pass) = (0.05 x 0.5) / (0.05 x 0.5 + 0.95 x 0.05) = 0.025 / 0.0725 = **34.5%**. With 1 in 100: 0.005 / (0.005 + 0.0495) = **9.2%**. *Trading: most "significant" backtests are false when real edges are rare. This is why Harvey, Liu & Zhu ask for t > 3, and why you log every trial.*

5. P(6 losses) = (19/37)^6 = **1.83%**. EV = 100(1 - 0.0183) - 6300(0.0183) = **-Rs 17.35 per cycle**. With a fair 50/50 coin it would be exactly 0. Doubling never changes the sign of EV. *It feels safe because you win 98% of cycles; the 2% wipes out about 64 wins.* This is the shape of many "90% win rate" option-selling strategies.

6. P(at least 7 of 10) = (120 + 45 + 10 + 1)/1024 = 176/1024 = 17.2%, so **about 172 managers** look like stars by pure luck. *Trading: survivors of a big crowd always look skilled.*

7. **HH: 6 flips. HT: 4 flips.** When you're waiting for HT and you flip H then H, you're still one T away (progress kept). When you're waiting for HH and you flip H then T, you're back to the start (progress lost). Overlap structure changes waiting times. *Trading: "same probability per step" doesn't mean "same time until it happens".*

8. **Expected price = Rs 100** (each day the expected multiplier is 0.5(1.01) + 0.5(0.99) = 1). **Median ~ Rs 98.76** = 100 x (1.01 x 0.99)^125 = 100 x 0.9999^125. Volatility drags the typical path below the average path. A few lucky paths pull the mean up. *This is the doorway to Kelly and ruin on Day 3.*

9. (a) **6**, by linearity of expectation (works even if they're dependent). (b) Independent: Var = 10 x 0.6 x 0.4 = **2.4** (SD 1.55). (c) Perfectly correlated: the count is either 10 or 0, so Var = 10^2 x 0.6 x 0.4 = **24** (SD 4.9). *Trading: 10 correlated stocks behave like 1 stock. Diversification depends on correlation, not on the count.*

10. E[max of 2 dice] = sum over k of k x (2k-1)/36 = 161/36 = **Rs 4.47**. **Buy** at 4.25: edge = **Rs 0.22 per trade**, about 5%. You'd sell above 4.47 (in practice quote around 4.30 bid / 4.65 ask, so you're paid for the risk). *Trading: a market maker's quote = fair value +/- a margin for risk and for the chance the other side knows more.*

**Scoring:** count how many gut guesses landed within 10% of the right answer. Write that number in your log. We'll track it all month.
