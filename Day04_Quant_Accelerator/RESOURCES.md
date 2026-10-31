# Day 4 resources: real returns, volatility, correlation, fat tails
All free. ✅ = in this ZIP. Links checked 31 Oct 2026.

## 1. Stylized facts and fat tails (folder 01)
- ✅ Rama Cont (2001), "Empirical properties of asset returns: stylized facts and statistical issues", Quantitative Finance. **Core reading.**
- ✅ Sargent & Stachurski, QuantEcon: "Heavy-Tailed Distributions" (PDF of the lecture). Live version with runnable code: https://intro.quantecon.org/heavy_tails.html
- ✅ Nassim Taleb, *Statistical Consequences of Fat Tails* (3rd ed., arXiv 2001.10488). Read the opening overview only today. https://arxiv.org/abs/2001.10488

## 2. Volatility (folder 02)
- ✅ Robert Engle (2001), "GARCH 101: The Use of ARCH/GARCH Models in Applied Econometrics", Journal of Economic Perspectives
- ✅ Robert Engle (2003), Nobel Lecture: "Risk and Volatility: Econometric Models and Financial Practice"
- ✅ MIT 15.450 *Analytics of Finance*, Leonid Kogan: Lecture 10 slides, *Volatility Models*
- Allan Malz (Columbia), lecture notes: *Volatility behavior and forecasting* (EWMA vs GARCH, clear). https://www.columbia.edu/~amm26/lecture%20files/volatilityBehaviorForecasting.pdf

## 3. Data (folder 03)
- ✅ 6 CSVs, 2007–2026 (see `README_DATA.md`)
- NSE / Nifty Indices official historical data, including the **NIFTY 50 Total Return Index**: https://www.niftyindices.com/reports/historical-data
- yfinance (what I used): https://github.com/ranaroussi/yfinance
- jugaad-data (Python, pulls NSE data directly; useful as a second source to cross-check): https://github.com/jugaad-py/jugaad-data

## 4. Video lectures
MIT 18.S096 *Topics in Mathematics with Applications in Finance* (Fall 2013), free. Full playlist: https://www.youtube.com/playlist?list=PLUl4u3cNGP63ctJIEC1UnZ0btsphnnoHR
1. Lecture 9, *Volatility Modeling* (historical vol, GBM, jumps). **Watch today.** https://www.youtube.com/watch?v=cDlbEQz1PQk
2. Lecture 8, *Time Series Analysis I* (stationarity, autocorrelation). https://www.youtube.com/watch?v=uBeM1FUk4Ps
3. Lecture 11, *Time Series Analysis II* (ARCH/GARCH). https://www.youtube.com/watch?v=_IFUfFuyQlU
4. Lecture 7, *Value At Risk (VAR) Models*: for problem 4. https://www.youtube.com/watch?v=92WaNz9mPeY
Course page with notes and problem sets: https://ocw.mit.edu/courses/18-s096-topics-in-mathematics-with-applications-in-finance-fall-2013/

## 5. Blogs (practitioner view)
- Rob Carver, *Is predicting vol better worth the effort, and does the VIX help?* (2025): simple EWMA vol vs fancy models, tested. https://qoppac.blogspot.com/2025/11/is-predicting-vol-better-worth-effort.html
- Rob Carver, *The relationship between ATR and standard deviation*: why recent weeks of vol forecast the next weeks best. https://qoppac.blogspot.com/2018/12/the-relationship-between-atr-and.html
- Rob Carver, *How much risk should we take?*: links Day 3 (Kelly) to today (vol targets). https://qoppac.blogspot.com/2020/03/how-much-risk-should-we-take.html

## 6. GitHub
- bashtage/arch: the standard Python GARCH library. Try it in Week 3, not today. https://github.com/bashtage/arch, docs: https://arch.readthedocs.io/en/latest/univariate/univariate_volatility_modeling.html
- Your repo **nifty50-sma-backtester**: today, add a `data_audit.py` that runs your checklist on its data. Your old backtest may have used the price index; note that.

## 7. Built for you (folder 04)
- `nifty_stats_lab.py` / `.ipynb`: tested on this data. Reference chart `nifty_stats_lab.png`.
  0. Data audit (finds and removes the Dec 2019 ETF errors)
  1. Simple vs log returns
  2. Vol: by year, rolling, clustering (ACF), leverage effect
  3. Fat tails: sigma table, Q-Q, log-scale histogram
  4. Correlation: matrix, time-zone trap, rolling, calm vs stress
  5. Price index vs ETF

## 8. Books for later
- John Hull, *Risk Management and Financial Institutions* (chapters on volatility, EWMA/GARCH, VaR and expected shortfall).
- Benoit Mandelbrot & Richard Hudson, *The (Mis)Behavior of Markets*: fat tails told as a story.
- Ruey Tsay, *Analysis of Financial Time Series*: the reference text, when you need the maths.
