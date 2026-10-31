# Day 6 resources: market microstructure
All free. ✅ = in this ZIP. Links checked 31 Oct 2026.

## 1. Foundations (folder 01)
- ✅ Glosten & Milgrom (1985), "Bid, Ask and Transaction Prices in a Specialist Market with Heterogeneously Informed Traders", JFE. **The adverse-selection model. Core reading.**
- ✅ Kyle (1985), "Continuous Auctions and Insider Trading", Econometrica. Kyle's lambda.
- ✅ Joel Hasbrouck, *Empirical Market Microstructure*: teaching notes, NYU Stern (draft 1.1, 2003). The best free textbook-style treatment: Roll model, sequential trade, and more.
- ✅ Gould, Porter, Williams, McDonald, Fenn & Howison (2013), "Limit Order Books", Quantitative Finance (arXiv). The LOB survey.
- ✅ Biais, Glosten & Spatt (2005), "Market Microstructure: A Survey of Microfoundations, Empirical Results, and Policy Implications".
- ✅ Bouchaud, Farmer & Lillo (2008), "How Markets Slowly Digest Changes in Supply and Demand" (arXiv). Price impact and the square-root law. A long reference: read sections 1–2.

## 2. Market making (folder 02)
- ✅ Avellaneda & Stoikov (2008), "High-frequency trading in a limit order book" (author preprint). Inventory skew, reservation price.

## 3. Spread, impact, execution (folder 03)
- ✅ Roll (1984), "A Simple Implicit Measure of the Effective Bid-Ask Spread in an Efficient Market", JF.
- ✅ Corwin & Schultz, "A Simple Way to Estimate Bid-Ask Spreads from Daily High and Low Prices" (NBER conference version; published in JF 2012).
- ✅ Almgren & Chriss (2000), "Optimal Execution of Portfolio Transactions". The cost vs risk trade-off when splitting an order.
- ✅ Cont, Kukanov & Stoikov (2014), "The Price Impact of Order Book Events" (arXiv). Order-flow imbalance.

## 4. NSE rules (folder 04)
- ✅ NSE FAQ: Pre-open Session in the Equity (CM) Segment (Oct 2026 version).
- ✅ NSE Capital Market Consolidated Circular (Apr 2026). Trading hours, order types, price bands, and tick sizes (§3.3). Note that ETFs are excluded from the price-linked tick table, so check the ETF's tick in the security file or on Kite.
- NSE pre-open session page: https://www.nseindia.com/static/products-services/equity-market-pre-open
- NSE market timings: https://www.nseindia.com/static/market-data/market-timings

## 5. Video and courses
- **UCPH, *Financial Markets Microstructure*** (Masters course, spring 2020, full YouTube playlist, CC-licensed): https://www.youtube.com/playlist?list=PL4pUs4P_j1Wa2_P1lw44kFWWjKDTGUY7S
  - Lecture 1, Concepts and Institutions: https://www.youtube.com/watch?v=nPqat782ADI
  - Lecture 2, Measuring Liquidity: https://www.youtube.com/watch?v=8hYE-QMI2Yg
  - Then the Glosten–Milgrom and Kyle lectures in the same playlist (lecture list: https://quantfinance.substack.com/p/financial-markets-microstructure)
- Dale Rosenthal, *Market Microstructure and Electronic Trading* course page, with R code for the Glosten–Milgrom and Kyle models: https://sites.google.com/site/dalerosenthal/teaching/market-microstructure
- Institut Louis Bachelier, *Practical Introduction to Market Microstructure* MOOC (17 short videos): https://mooc.institutlouisbachelier.org/en/mooc/practical-introduction-to-market-microstructure-2/

## 6. GitHub
- Your own **Rubin-S/orderbook**: today's lab exports a session in its replay format.
- jpmorganchase/abides-jpmc-public: an agent-based exchange simulator (market makers, noise and informed agents). For later, if you want to scale up today's toy. https://github.com/jpmorganchase/abides-jpmc-public
- nkaz001/hftbacktest: a backtester that models queue position and latency. Read its README to see what "realistic fills" requires. We won't use it, since we trade daily. https://github.com/nkaz001/hftbacktest

## 7. Built for you (folder 06)
- `naive_mm_lab.py` / `.ipynb` + reference chart `naive_mm_lab.png`:
  - A–B: naive market maker vs informed and noise traders, with the P&L split
  - C: markouts
  - D: break-even spread vs the share of informed traders
  - E: fixes (learning from order flow, inventory skew)
  - F: NIFTYBEES spread estimated from daily data (Roll, Corwin–Schultz) vs the 1-tick floor
  - G: session export for your C++ engine
- `naive_mm_session.csv` + `naive_mm_session_truth.csv` + `pnl_from_replay.py`.

## 8. Books for later
- Larry Harris, *Trading and Exchanges* (2003): the practitioner bible. Chapters on dealers, informed traders and liquidity.
- Bouchaud, Bonart, Donier & Gould, *Trades, Quotes and Prices* (2018).
- Cartea, Jaimungal & Penalva, *Algorithmic and High-Frequency Trading* (2015).
