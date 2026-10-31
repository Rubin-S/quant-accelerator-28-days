# Day 15 resources (checked 31 Oct 2026). ✅ = in this ZIP

## Papers (01_papers)
- ✅ Harvey, Hoyle, Korgaonkar, Rattray, Sargaison & Van Hemert (2018), "The Impact of Volatility Targeting," JPM 45(1): helps Sharpe for risk assets (via the leverage effect) and thins the left tail.
- ✅ Moreira & Muir (2017), "Volatility-Managed Portfolios," NBER w22208 (JF version 2017).
- ✅ J.P. Morgan/Reuters (1996), *RiskMetrics Technical Document*, 4th ed.: EWMA and λ = 0.94 for daily data.
- Already in earlier kits, so not repeated: Chan ch. 1 (Day 9), Harvey & Liu *Backtesting* (Day 5), Arnott-Harvey-Markowitz protocol (Day 10), Frazzini-Israel-Moskowitz costs (Day 7).

## Architecture: free articles
- QuantStart, *Event-Driven Backtesting with Python*, Parts I–VIII (Part I): https://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-I
  Part II (events): https://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-II · Part IV (strategy): https://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-IV/ · Part VII (performance): https://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-VII/
- QuantStart, "Backtesting Systematic Trading Strategies in Python: Considerations and Open Source Frameworks": https://www.quantstart.com/articles/backtesting-systematic-trading-strategies-in-python-considerations-and-open-source-frameworks
- Scott Rome, "Build Your Own Event-Based Backtester in Python": http://srome.github.io/Build-Your-Own-Event-Based-Backtester-In-Python/

## Video
- Michael Halls-Moore, "When Should You Build Your Own Backtester?" (QuantCon 2016). Event-driven design starts around 28:09: https://www.youtube.com/watch?v=OhGdVdolqkU

## GitHub (read the code, don't adopt it wholesale)
- quantstart/qstrader (the portfolio/position-sizer split): https://github.com/quantstart/qstrader
- tobiasbrodd/backtester (runnable version of the QuantStart series): https://github.com/tobiasbrodd/backtester
- robcarver17/pysystemtrade (vol-targeted position sizing done properly; huge, so read `sysquant` and the sizing code): https://github.com/robcarver17/pysystemtrade
- nautechsystems/nautilus_trader (same code for backtest and live; the Week 4 idea): https://github.com/nautechsystems/nautilus_trader

## Testing
- Hypothesis (property-based testing) docs: https://hypothesis.readthedocs.io

## Build-along (03_build_along), all tested here
- `engine.py`, plus `test_engine.py` (17 tests incl. a Hypothesis property test: `pip install pytest hypothesis`), `run_demo.py`/`.ipynb`, `nse_costs.py` (Day 7)
