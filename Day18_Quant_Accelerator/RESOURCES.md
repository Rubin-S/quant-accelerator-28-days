# Day 18 resources (checked 31 Oct 2026). ✅ = in this ZIP

## Papers
- ✅ Bergmeir, Hyndman & Koo (2018), "A Note on the Validity of Cross-Validation for Evaluating Autoregressive Time Series Prediction," *CSDA* 120 (author working paper). When shuffled K-fold is OK for time series and when it isn't. Read sections 1, 2 and 5.
- Hansen (2005), "A Test for Superior Predictive Ability," *JBES* 23(4). Open copy at the UNC repository: https://cdr.lib.unc.edu/concern/articles/hd76s214m (my sandbox couldn't reach it; open it on your laptop). It asks whether the *best* of many rules beats a benchmark after paying for the search. `walk_forward.py` runs it via `arch`.
- White (2000), "A Reality Check for Data Snooping," *Econometrica* 68(5), DOI 10.1111/1468-0262.00152 (paywalled; Hansen section 1 summarises it).
- Pardo, *The Evaluation and Optimization of Trading Strategies* (2nd ed., Wiley 2008), ch. 11 "Walk-Forward Analysis" (book, not free; the podcast below covers it).

## Already in earlier kits (re-read, not repeated)
- Bailey et al., *Probability of Backtest Overfitting* (CSCV): Day 5. That's the combinatorial cousin of today's walk-forward.
- Arnott, Harvey & Markowitz, *A Backtesting Protocol*: Day 10. Re-read the "cross-validation" and "model dynamics" items.
- Harvey & Liu, *Backtesting* (haircuts): Day 5.

## Videos and podcasts
- *The Algorithmic Advantage* ep. 035, Bob Pardo Part II: "Building Trading Strategies that Work with Walk Forward Analysis" (2025). The inventor explains WFA, walk-forward efficiency, and window sizing. https://www.youtube.com/watch?v=Y6cbSyCtKz0
- Chad Thackray, "Walk Forward Optimization in Python with Backtesting.py" (code-along, ~1 h). Watch it for mechanics, then notice that it re-optimises freely, which your pre-reg forbids. https://www.youtube.com/watch?v=9m987swadQU
- Ernest Chan, "What is the risk of overfitting a single asset time series?" (short): https://www.youtube.com/watch?v=S5Qk8WJjehQ

## Blogs and guides (free)
- Rob Carver, "The three kinds of (over) fitting": explicit, implicit, tacit; expanding vs rolling windows. https://qoppac.blogspot.com/2015/11/the-three-kinds-of-overfitting.html
- Rob Carver, "Breaking Badly: finding the structural breaks in parameter estimates" (June 2026): how many years in-sample before a refit helps. https://qoppac.blogspot.com/2026/06/breaking-badly-finding-structural.html
- Rob Carver, "Trading strategies that are designed, not fitted" (slides). Real data is used only for a sensitivity check. https://www.slideshare.net/slideshow/trading-strategies-that-are-designed-not-fittedby-robert-carver-independent-systematic-futures-trader-writer-and-research-consultant/75640564
- Better System Trader ep. 60 with Robert Pardo (show notes): https://bettersystemtrader.com/060-strategy-optimization-with-robert-pardo/
- Hyndman & Athanasopoulos, *Forecasting: Principles and Practice* (3rd ed., free online), §5.10 "Time series cross-validation": https://otexts.com/fpp3/tscv.html

## Code and docs
- `arch` multiple-comparison procedures (SPA, StepM, MCS): https://bashtage.github.io/arch/multiple-comparison/multiple-comparisons.html
- scikit-learn `TimeSeriesSplit` (expanding-window splitter; note its `gap` argument): https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html
- Rob Carver's `pysystemtrade` (expanding-window fitting in production code): https://github.com/robcarver17/pysystemtrade

## Build-along (03_build_along), all run and tested here
- `walk_forward.py`: WF selection (expanding + rolling 5y) over the pre-registered grid, walk-forward efficiency, year × lookback heat map, 6–14m plateau heat map, Hansen SPA, and **start-date stability**. ~10 s.
- `test_walk_forward.py`: 5 tests, including "the pick for year y can't see year y". `test_is_report.py`: Day 17's 6 tests (11 in total, all passing).
- `wf_out/`: the demo stability report and 4 charts.
