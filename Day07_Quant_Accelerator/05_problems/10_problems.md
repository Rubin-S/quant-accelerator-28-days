# Day 7: 10 problems on the cost stack
Use only the rates in 01_official_rates/RATES_SNAPSHOT. Do these BY HAND first, then check them with nse_costs.py.
Rules: gut guess → worked answer → one-line trading implication.

1. **Delivery share, ₹50,000.** Buy ₹50,000 of a stock (delivery) and sell it later at ₹50,000. Zerodha. List every charge and the total. What % of the total is STT?

2. **Same money, NIFTYBEES.** The same round trip at ₹1,00,000 in NIFTYBEES (an equity ETF, delivery). Total? Why so much cheaper than a share?

3. **Intraday, ₹2 lakh.** Buy and sell ₹2,00,000 of a stock intraday (MIS), same day. Total costs?

4. **Breakeven.** For problem 3, what % move do you need just to break even (ignoring spread)? If you do that trade 250 days a year, what's the annual cost in % of ₹2 lakh?

5. **The GST trap.** Is GST charged on STT? On stamp duty? Recompute problem 1's GST if someone wrongly applied 18% to everything. How big is the error?

6. **Small account.** A ₹5,000 NIFTYBEES round trip (delivery). Round-trip cost in bps? Why is it 8× worse than at ₹1 lakh?

7. **The rate change.** Before 1 Mar 2026 the NSE charge was ₹297 + ₹10 IPFT per crore. After, ₹306.99 + ₹0.01. Did your cost change? Why did NSE do it?

8. **Tax is a cost.** You make a ₹20,000 gain on NIFTYBEES. Tax if you sell after 3 months? After 13 months (assume no other LTCG this year)? What does this do to a strategy that trades monthly?

9. **Annual drag.** A strategy does 24 round trips a year in NIFTYBEES with ₹1 lakh. Statutory + DP ≈ 3.9 bps per round trip; assume spread + slippage 2 bps per round trip. Annual drag in %? What if it's 250 round trips?

10. **Contract note check.** Your ₹1 lakh delivery round trip in a share has a contract note total (all charges) of ₹223.00. Your calculator says ₹237.82. Is your calculator 6.6% wrong? Find the real explanation before you "fix" anything.
