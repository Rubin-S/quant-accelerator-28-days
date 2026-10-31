# Solutions. Don't open until all 10 are attempted.

1. 1.29% × √252 = **20.5%** a year; weekly 1.29% × √5 = **2.9%**. Variances add across independent days (so 252 × variance), and vol is the square root of variance, so it scales with √time. *Every vol number you ever compare must be on the same clock.*

2. 1.10 × 0.90 = 0.99, so **−1%**. In logs: ln(1.1) + ln(0.9) = 0.0953 − 0.1054 = **−0.0101**. +50% then −50% = 1.5 × 0.5 = 0.75, so **−25%**. *The same volatility drag as Day 3. Volatile paths cost you money even when the "average" move is zero.*

3. 13.9 / 1.29 ≈ **10.8 sigma**. Under a normal model, a 10.8-sigma day has a probability of about 3 in 10^27: not once in the age of the universe. It happened in your lifetime, and NIFTY had 7 days beyond 6 sigma in 19 years. *The normal model isn't slightly wrong in the tails, it's wrong by many orders of magnitude. Never set a risk limit from a normal sigma alone.*

4. (a) 2.326 × 1.29% ≈ 3.00%, so **Rs 3,000**. (b) **Rs 3,620**. (c) **Rs 5,460**. Use the **expected shortfall** (or a stress loss even bigger, like the −13.9% day = Rs 13,900): VaR says where the bad days *start*, not how bad they get. *Size so that the worst day in the data, not the 99% line, is survivable.*

5. Expected at 1%: 46.9 breaches, sd ≈ √(4690 × 0.01 × 0.99) ≈ 6.8. Observed: 1.79% × 4690 ≈ 84 breaches, about **(84 − 47)/6.8 ≈ 5.4 sd too many**. Not close: the normal model is rejected. *A "99%" model that fails twice as often is how risk managers get fired.*

6. 20.5% / √12 = **5.9%** per month, which annualises back to 20.5%; the data gave 20.7%. Agreement means returns are close to uncorrelated across days, so √time roughly works for NIFTY at these horizons. It breaks when returns trend or mean-revert (autocorrelation), and for strategies like option selling where risk hides until it doesn't. *Check √time on your own strategy's returns. If monthly vol is much bigger than daily × √21, you have hidden trend risk.*

7. σp = √(0.25·17.9² + 0.25·15.8² + 2·0.25·(−0.01)·17.9·15.8) = √(80.1 + 62.4 − 1.4) ≈ **11.9%**. Below both because the two barely move together, so their bad days partly cancel. *Diversification is the only free lunch, but correlations move (lab plot 4). Don't plan on a correlation that only holds in calm markets.*

8. 12% / 30% = **0.40, so 40%** of capital. At 9% vol, 12/9 = 1.33x, but the cap says **1.0x**. *Vol targeting cuts size automatically when markets get wild, which is when fat tails hit. It's Kelly's logic (bet ∝ 1/σ²) made practical.*

9. The S&P's session on date t starts after NSE closes. At NSE's close you **don't know** today's S&P move, so the backtest is using future information (look-ahead). Live, the signal isn't available until your time is past, so the edge **vanishes**. *Before trusting any cross-market signal, write down the exact timestamp (in IST) when each input becomes known.*

10. Mostly **dividends**: the price index ignores them; the ETF's value includes the dividends of the stocks it holds, minus fees and tracking error. (Check NSE's NIFTY 50 Total Return Index to confirm the size.) Backtesting on the price index **understates** a buy-and-hold you could really own, by roughly 1%/yr here. So if your strategy sits in cash part of the time, comparing it to the price index flatters it. *Benchmark against the Total Return Index or the ETF, never the price index.*
