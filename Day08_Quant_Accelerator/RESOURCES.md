# Day 8 resources: edge families
✅ = in this ZIP (author/working-paper copies, free). Checked 31 Oct 2026.

## 1. Trend and momentum (folder 01)
- ✅ Moskowitz, Ooi & Pedersen (2012), "Time Series Momentum", JFE. **The core paper for your realistic family.**
- ✅ Hurst, Ooi & Pedersen (2017), "A Century of Evidence on Trend-Following Investing", JPM.
- ✅ Asness, Moskowitz & Pedersen (2013), "Value and Momentum Everywhere", JF.
- ✅ Jegadeesh & Titman (2001), "Profitability of Momentum Strategies: An Evaluation of Alternative Explanations" (NBER WP).
- AQR's data for the TSMOM paper: https://www.aqr.com/Insights/Datasets/Time-Series-Momentum-Original-Paper-Data
- TSMOM slides by the authors: http://docs.lhpedersen.com/TSMOM_Slides.pdf

## 2. Mean reversion and pairs (folder 02)
- ✅ Gatev, Goetzmann & Rouwenhorst (2006), "Pairs Trading: Performance of a Relative-Value Arbitrage Rule" (Yale WP).
- ✅ Lo & MacKinlay (1990), "When Are Contrarian Profits Due to Stock Market Overreaction?" (NBER WP). Explains why index returns look autocorrelated (stale prices).

## 3. Carry and events (folder 03)
- ✅ Koijen, Moskowitz, Pedersen & Vrugt, "Carry" (working paper).
- ✅ Lou, Polk & Skouras (2019), "A Tug of War: Overnight versus Intraday Expected Returns", JFE.
- Jain & Dua (2021), "Evaluation of Different Seasonal Anomalies in the Indian Equity Market" (NIFTY 1990–2021; effects fading in recent years): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3984188

## 4. India evidence (folder 04)
- ✅ Agarwalla, Jacob & Varma, "Four Factor Model in Indian Equities Market" (IIMA WP).
- ✅ IIMA Indian Fama-French-Momentum data library, release 2025-12 (monthly + yearly CSVs, incl. survivorship-adjusted). Live library: https://faculty.iima.ac.in/iffm/Indian-Fama-French-Momentum/
- ✅ NSE Indices, Nifty200 Momentum 30 methodology whitepaper (Sep 2020). Several NSE-listed ETFs track this index (e.g. MOM30IETF, MOMOMENTUM).

## 5. Where edges die (folder 05)
- ✅ McLean & Pontiff (2016), "Does Academic Research Destroy Stock Return Predictability?", JF: 26% lower out-of-sample, 58% lower post-publication.
- ✅ Lo (2004), "The Adaptive Markets Hypothesis", JPM.
- ✅ Kakushadze & Serur, "151 Trading Strategies" (361 pp): a catalogue to browse for card ideas. Most strategies won't fit our rules; checking WHY is the exercise.
- (Day 5's ZIP already has Harvey-Liu-Zhu, "...and the Cross-Section of Expected Returns".)

## 6. Videos
- Toby Moskowitz (AQR/Yale): systematic investing and trend following: https://www.youtube.com/watch?v=fiQiFtUV4iE
- Cliff Asness: momentum in a few minutes: https://www.youtube.com/watch?v=TM3qYdb8lQo
- Aswath Damodaran (NYU), Session 9: Random Walks and Momentum: https://www.youtube.com/watch?v=T3WoIU8_ebQ
- Ernie Chan (QuantInsti): mean reversion trading: https://www.youtube.com/watch?v=sFwyS-L-aDE
- Quantopian lecture: p-hacking and multiple comparisons: https://www.youtube.com/watch?v=YiDfbYtgUPc

## 7. GitHub
- Quantopian lecture notebooks (pairs trading, mean reversion, overfitting; free): https://github.com/quantopian/research_public/tree/master/notebooks/lectures
- Hudson & Thames arbitrage_research (pairs approaches: distance, cointegration, copula), notebooks: https://github.com/hudson-and-thames/arbitrage_research

## 8. Built for you (folder 06), tested
- `edge_family_explorer.py` / `.ipynb` + chart: 8 pre-declared tests, 2007–2018 only, robust t-stats, trial count.
- `india_factor_facts.py`: IIMA factor stats; momentum by era.

## 9. Templates (folder 08)
- `idea-card-template.md` (with a 30-point score), `example-idea-card-FILLED.md`.
