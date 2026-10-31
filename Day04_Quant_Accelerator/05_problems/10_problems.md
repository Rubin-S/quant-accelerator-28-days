# Day 4: 10 problems on real NIFTY numbers
Same rules: gut guess → worked answer → one-line trading implication. Solutions only after all 10.
Facts from the lab (NIFTY 50, 17 Sep 2007 – 30 Oct 2026, 4,690 daily log returns):
daily vol 1.29%, annualised 20.5%; worst day −13.9% (23 Mar 2020); excess kurtosis 15.2.

1. **Annualise.** Daily vol is 1.29%. What's the annual vol? The weekly vol? Why √252 and not 252?

2. **Up then down.** NIFTY rises 10% one day and falls 10% the next. Where does it end, in % and in log terms? What about +50% then −50%?

3. **How impossible was March 2020?** Using daily vol 1.29% and a normal distribution, how many sigmas was the −13.9% day? Roughly how often should that happen under a normal model?

4. **VaR two ways.** Rs 1,00,000 in NIFTY. (a) Normal 99% one-day VaR = 2.326 × daily vol. In rupees? (b) The actual 1% worst-day cutoff in the data is −3.62%. In rupees? (c) The average loss on those worst 1% of days (expected shortfall) is −5.46%. Which of the three numbers should your risk limit use?

5. **Breaches.** A good 99% VaR model should be breached on about 1% of days. On NIFTY, the normal-model VaR was breached on 1.79% of days. Is that close enough? What would 4,690 days at 1% look like (expected count and rough standard deviation)?

6. **Square-root-of-time.** Annual vol is 20.5%. What does √time predict for monthly vol? Measured monthly-return vol × √12 came out at 20.7%. What does that agreement tell you, and what could break it?

7. **Diversification.** Since 2009: NIFTY vol 17.9%, gold ETF vol 15.8%, correlation about −0.01. What's the vol of a 50/50 portfolio? (The data gives 11.9%.) Why is it lower than both?

8. **Vol targeting.** Your rule: target 12% annual vol, max 1.0x. Today NIFTY's 21-day vol is 30%. What fraction of capital goes into NIFTY? What if vol is 9%?

9. **Time zones.** NIFTY vs S&P 500 same-date correlation is +0.29; NIFTY today vs S&P yesterday is +0.23. A friend's backtest buys NIFTY at today's close whenever the S&P is up "today". What's wrong, and what will happen live?

10. **Price vs what you earn.** Since 2010 the NIFTY 50 price index grew at 9.19% a year; the NIFTYBEES ETF at 10.04%. What explains most of the gap? If you backtest on the price index, is your strategy's return biased up or down vs a buy-and-hold you could really own?
