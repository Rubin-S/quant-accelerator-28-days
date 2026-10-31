# Day 8: 10 problems on edge families
Gut guess → worked answer → one-line trading implication. No code needed.

1. **Time-series vs cross-sectional momentum.** Explain the difference in two lines. Which one can you trade with a single ETF, long/flat?

2. **Who's on the other side?** For each family (trend, mean reversion, carry, event, pairs), name the counterparty who loses on average and why they keep doing it.

3. **Carry for a cash-only trader.** Koijen et al. define carry as the return if prices don't change. What's the carry of holding NIFTYBEES? Of a liquid-fund ETF? Why is "carry" mostly closed to us?

4. **The decay haircut.** A paper reports 10% a year for a strategy. Using McLean-Pontiff (26% lower out-of-sample, 58% lower post-publication), what should you expect now? What does that do to a strategy that also costs 4% a year to run?

5. **Turnover kills.** Novy-Marx & Velikov find few anomalies above 50% monthly turnover survive costs. Convert: a strategy that flips its whole position every week has roughly what monthly turnover?

6. **Pairs ≠ correlation.** NIFTY and NIFTYBANK have a daily return correlation of about 0.88 (2007–2018), yet the explorer's spread had a half-life of 403 days and failed Dickey-Fuller. How can both be true?

7. **The robust t.** The explorer's daily autocorrelation had naive t = 3.99 but robust t = 2.20. Explain why volatility clustering inflates the naive t.

8. **Eight tests.** You ran 8 independent-ish tests. The best has |t| = 2.49. Is that evidence? (Use Day 5: the expected maximum of 8 |N(0,1)| draws.)

9. **The locked sample.** Why is it worse to glance at a 2021 chart of your idea than to never test it at all?

10. **India momentum.** The IIMA WML factor earned about 13% a year with a −53% worst drawdown. Name three reasons you can't harvest it in this program, and one honest way part of the idea might still reach an ETF trader.
