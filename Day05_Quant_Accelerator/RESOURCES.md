# Day 5 resources: overfitting, multiple testing, deflated Sharpe
All free. ✅ = in this ZIP. Links checked 31 Oct 2026.

## 1. Core papers (folder 01)
- ✅ Bailey, Borwein, López de Prado & Zhu (2014), "Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample Performance", Notices of the AMS (preprint). **MinBTL. Read first.**
- ✅ Bailey & López de Prado (2014), "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality", Journal of Portfolio Management (preprint). **Read second.**
- ✅ Bailey, Borwein, López de Prado & Zhu (2017), "The Probability of Backtest Overfitting", Journal of Computational Finance (preprint). The CSCV method.
- ✅ Bailey & López de Prado (2012), "The Sharpe Ratio Efficient Frontier": the Probabilistic Sharpe Ratio (PSR) and Minimum Track Record Length. The maths under DSR.

## 2. Multiple testing (folder 02)
- ✅ Harvey & Liu (2014), "Evaluating Trading Strategies", JPM. Short and readable; the best starting point.
- ✅ Harvey & Liu (2015), "Backtesting", JPM: the Sharpe "haircut".
- ✅ Harvey, Liu & Zhu (2016), "...and the Cross-Section of Expected Returns", RFS (NBER working paper). The t > 3 bar.
- ✅ Campbell Harvey, *Backtesting* lecture slides (Duke, 2024, 115 slides): the whole topic as a lecture.
- ✅ Ioannidis (2005), "Why Most Published Research Findings Are False", PLoS Medicine.

## 3. Video
- Marcos López de Prado, *Dangers of Backtest Overfitting* (talk). https://www.youtube.com/watch?v=QxhxLwNbMMg
- Hudson & Thames, *The 7 Sins of Backtesting*. https://www.youtube.com/watch?v=kUtRdaY59RU
- López de Prado's own lists of lectures and videos (including his Cornell ORIE 5256 course material and "7 Reasons Most ML Funds Fail"): https://www.quantresearch.org/Lectures.htm and https://www.quantresearch.org/Videos.htm

## 4. Interactive and blogs
- Bailey et al., *Backtest overfitting in financial markets*: describes their online Backtest Overfitting Demonstration Tool. https://www.davidhbailey.com/dhbpapers/overfit-tools-at.pdf
- Mathematical Investor blog (Bailey & Borwein): short essays on overfitting in finance. https://mathinvestor.org/
- López de Prado's software page (original CSCV / PBO code). https://www.quantresearch.org/Software.htm

## 5. GitHub
- esvhd/pypbo: PBO, PSR, MinTRL, MinBTL and DSR in Python. Use it to cross-check your own implementation. https://github.com/esvhd/pypbo
- CH4RL3I/fluke: small and clean: PBO (CSCV), DSR, MinTRL with a noise-vs-signal demo. https://github.com/CH4RL3I/fluke
- Your repo **nifty50-sma-backtester**: count how many parameter combinations you tried when you built it. Compute its DSR. Write the result in the README honestly.

## 6. Built for you (folder 04)
`overfitting_lab.py` / `.ipynb` (tested on the NIFTY data; reference chart `overfitting_lab.png`):
1–2. 20 coin-flip strategies on real NIFTY, IS vs OOS
3. 2,000 contests vs the False Strategy Theorem
4. Best fake Sharpe vs number of trials
5. Deflated Sharpe Ratio
6. PBO via CSCV (12,870 splits)
7. MinBTL table
8. Control experiment with one real edge planted

## 7. Books for later
- Marcos López de Prado, *Advances in Financial Machine Learning* (2018): chapters 11–14 on backtesting dangers, CPCV and backtest statistics.
- López de Prado, *Machine Learning for Asset Managers* (2020): section 8, testing set overfitting.
- David Aronson, *Evidence-Based Technical Analysis* (2006): data-mining bias, explained for traders.
