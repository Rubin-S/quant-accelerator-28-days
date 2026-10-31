# Solutions. Don't open until all 10 are attempted.

1. Spread = ₹0.01 on mid ₹261.875 = **0.38 bps**. Round trip at those quotes: lose one full spread on ₹10,00,000 × 0.0000382 ≈ **₹38**, before brokerage, STT and fees (which can easily be bigger for an ETF this liquid). *For liquid index ETFs, the spread is the small cost. Check your broker's charges sheet: they may dominate.*

2. P(buy | V=101) = μ + (1−μ)/2 = 0.6; P(buy | V=99) = 0.4. So ask = (0.6·101 + 0.4·99)/(0.6+0.4) = **₹100.20**, bid = **₹99.80**, spread **₹0.40**. In general ask = 100 + μ, so at μ = 50%: **₹100.50 / ₹99.50, spread ₹1.00**. *The spread is the price of trading with people who might know more. More informed flow means wider spreads, even with zero costs and zero profit for the MM.*

3. Spread = 2·√0.0004 = 2 × 0.02 = **₹0.04**. *Bid-ask bounce makes prices look mean-reverting at very short horizons. A "reversal strategy" on close-to-close data can just be harvesting a spread you can't actually earn.*

4. At fill: you paid ₹100.00 vs mid ₹100.01, so **+1 paisa** (you bought below mid, so you were the one quoting). At 1 minute: 99.97 − 100.00 = **−3 paise**. A bad fill: it looked fine at the moment, but the market moved through you. That's adverse selection. *Judge fills by where the price goes after, not by the price you got.*

5. 1.3% × √0.01 = 1.3% × 0.1 = **0.13% = 13 bps**. At 10%: 1.3% × √0.1 ≈ **41 bps**. Ten times the size costs about 3× as much per unit (the square-root law; Bouchaud, Farmer & Lillo survey the evidence). *At our tiny size, impact is negligible. It's a capacity limit you'd hit long before you're rich.*

6. 50,000 / 5,000 = **10 minutes** if no one ahead cancels and the price stays put. You're most likely filled in a minute when **heavy selling sweeps the bid**, i.e. just before the price drops. Passive orders get filled when you least want them (adverse selection), and they DON'T get filled when the price runs away from you. *A limit order isn't free: it trades spread for adverse selection and missed trades.*

7. Market order: 0.2 bps. Limit order: 0.3 × 20 bps = **6 bps** expected cost of chasing (ignoring the half-spread saved on the other 70%: about 0.14 bps). **The market order is far cheaper here.** *For a liquid ETF and a slow signal, pay the tiny spread. Our plan sends limit orders only, so use a marketable limit: a limit at or slightly through the ask.*

8. r = 100 − 10 × 0.1 × 0.04 = **₹99.96**. Both quotes shift **down**. A lower ask makes it more likely you sell (shrinking the long inventory); a lower bid makes it less likely you buy more. *Inventory is risk. A good market maker pays a little to get rid of it.*

9. At ₹261.80: demand 600, supply 150 → 150 trades. At ₹261.90: demand 300, supply 300 → **300 trades**. At ₹262.00: demand 100, supply 500 → 100. Opening price **₹261.90**, volume **300** (with zero imbalance). *The open is an auction, not a continuous market. Backtests that assume you trade "at the open" are pretending you were in this auction at that price.*

10. Half the edge = 2%/yr = 200 bps. At 10 bps per round trip: **20 round trips a year**. At 25 bps: **8**. *Costs decide the frequency of a strategy, not the other way round. Estimate costs pessimistically BEFORE you design the signal.*
