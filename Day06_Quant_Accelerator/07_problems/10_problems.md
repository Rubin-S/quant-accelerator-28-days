# Day 6: 10 problems on microstructure
Rules: gut guess → worked answer → one-line trading implication. Solutions after all 10.

1. **Spread in bps.** NIFTYBEES shows bid ₹261.87, ask ₹261.88. What's the spread in basis points of the mid? What does crossing it cost on a ₹10 lakh round trip (buy at ask, later sell at bid, same quotes)?

2. **Glosten–Milgrom by hand.** The true value is ₹101 or ₹99 (50/50). A fraction μ = 20% of traders are informed (buy if ₹101, sell if ₹99); the rest buy or sell 50/50. A competitive, risk-neutral market maker sets ask = E[V | a buy arrives] and bid = E[V | a sell arrives]. Find bid, ask, spread. Then do μ = 50%.

3. **Roll's estimator.** The covariance of consecutive price changes is −0.0004 (₹²). Estimated effective spread?

4. **Markouts.** You bought 1 unit at ₹100.00 when the mid was ₹100.01. One minute later the mid is ₹99.97. Your markout at fill and at 1 minute? Was this fill "good"?

5. **Square-root impact.** Daily vol 1.3%. You buy 1% of a day's volume. Using impact ≈ Y·σ·√(Q/V) with Y ≈ 1, what's the expected impact in bps? And for 10% of the day's volume?

6. **The queue.** You join the best bid with 50,000 units already ahead of you. About 5,000 units trade at that price per minute and nobody ahead cancels. How long until you're filled? Now: in which kind of minute are you MOST likely to finally get filled, and why is that bad?

7. **Market or limit?** Your daily NIFTYBEES strategy signals "buy" at 15:00. A market order pays half a spread now. A limit order at the bid saves that, but it doesn't always fill, and the price runs away on 30% of days by an average of 20 bps. The half-spread is 0.2 bps. Which is cheaper on average?

8. **Inventory skew (Avellaneda–Stoikov).** Reservation price r = s − q·γ·σ²·(T−t). Mid s = ₹100, inventory q = +10, γ = 0.1, σ²(T−t) = 0.04. Find r. Which way do your quotes move, and why does that help?

9. **NSE pre-open auction.** Buy orders: 100 @ ₹262.00, 200 @ ₹261.90, 300 @ ₹261.80. Sell orders: 150 @ ₹261.80, 150 @ ₹261.90, 200 @ ₹262.00. Using NSE's rule (the price that maximises executable volume), find the opening price and traded volume.

10. **The cost budget.** Your strategy's gross edge is 4% a year. All-in cost per round trip (spread + brokerage + STT/fees + impact) is 10 bps. How many round trips a year before costs eat HALF the edge? What if the true cost is 25 bps?
