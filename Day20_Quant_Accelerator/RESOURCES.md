# Day 20 resources: the one look (checked 1 Nov 2026). ✅ = in this ZIP

Read these BEFORE you seal your predictions. They tell you how much a backtest usually shrinks out of sample, which is the base rate your predictions should start from.

## Papers
- ✅ Falck, Rej & Thesmar (2021), "Why and How Systematic Strategies Decay" (arXiv 2105.01380; published in *Quantitative Finance* 2022 as "When do systematic strategies decay?"). Published anomalies keep about **half** their in-sample Sharpe out of sample. Read the intro + section 3.
- ✅ McLean & Pontiff (2016), "Does Academic Research Destroy Stock Return Predictability?" *JF* 71(1) (author working paper, 2012 version). Returns are **26% lower out of sample** and 58% lower after publication. Abstract + section on OOS vs post-publication.
- ✅ Hurst, Ooi & Pedersen (2017), "A Century of Evidence on Trend-Following Investing," *JPM* 44(1) (AQR copy). The out-of-sample case FOR trend: it worked across decades and in 8 of the 10 worst 60/40 crises. Your base rate for whether trend survives.
- Suhonen, Lennkh & Perez (2017), "Quantifying Backtest Overfitting in Alternative Beta Strategies," *JPM* 43(2). 215 bank strategies, median **73% Sharpe drop** from backtest to live; more complex = worse. Paywalled; free summary: https://alphaarchitect.com/looking-at-alternatives-avoid-complexity-and-magical-backtests

## Already in earlier kits: use them today
- Bailey & López de Prado, **Deflated Sharpe Ratio** (2014) and **PSR** (2012): Day 5 kit, `01_core_papers`. `holdout_report.py` implements both (cross-checked against Day 5's `overfitting_lab.py`).
- Bailey et al., PBO; Harvey & Liu, *Backtesting*: Day 5. Arnott-Harvey-Markowitz protocol: Day 10. Faber (2007/2013): Day 9.

## Videos
- Marcos López de Prado, "Dangers of Backtest Overfitting" (Day 5 link, re-watch the DSR part): https://www.youtube.com/watch?v=QxhxLwNbMMg
- The Algorithmic Advantage ep. 035, Bob Pardo Part II (Day 18): his take on what out-of-sample results can and can't prove. https://www.youtube.com/watch?v=Y6cbSyCtKz0

## Blogs (free)
- Alpha Architect summary of Suhonen et al. (above).
- CXO Advisory, "Live Performance of Alternative Beta Products": https://www.cxoadvisory.com/big-ideas/live-performance-of-alternative-beta-products
- AQR's page for the century paper: https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing

## Data
- OECD SDMX API, Short-term interest rates for India (IR3TIB), used for the 2019–2026 cash leg: dataflow `OECD.SDD.STES,DSD_STES@DF_FINMARK`, query `IND.M.IR3TIB.PA.....`
- RBI DBIE (91-day T-bill, the better cash leg): https://data.rbi.org.in

## Build-along (03_build_along), run and tested here (10 tests pass)
- `seal_predictions.py`: verifies your pre-reg lock, checks every prediction has a point + 90% interval, hashes them, and prints the holdout password.
- `holdout_report.py`: refuses to run if predictions changed after sealing, logs every opening, runs the pre-registered rule ONCE, then reports: falsifiers, bootstrap bands, PSR/DSR, your predictions graded (90%-interval hits + Brier), yearly table, charts.
- `demo/predictions.json`: my own predictions, written before my demo run. `demo/SEALED_mentor_demo_holdout_report.zip` holds my results (same password). Open it only AFTER your own run, to compare.
