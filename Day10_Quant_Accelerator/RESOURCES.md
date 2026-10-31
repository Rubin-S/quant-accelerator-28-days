# Day 10 resources (checked 31 Oct 2026)
✅ = in this ZIP.

## Why ideas die (folder 01)
- ✅ Hou, Xue & Zhang, "Replicating Anomalies" (Oct 2018 version of the RFS 2020 paper, from the authors' site). 452 anomalies: 65% fail |t| ≥ 1.96 and 82% fail the 2.78 hurdle. NBER page: https://www.nber.org/papers/w23394
- ✅ Novy-Marx & Velikov, "A Taxonomy of Anomalies and Their Trading Costs" (RFS 2016; Aug 2015 author version). Costs kill most strategies above about 50% monthly turnover.

## The other side (folder 02): read it so your scepticism is calibrated, not lazy
- ✅ Jensen, Kelly & Pedersen, "Is There a Replication Crisis in Finance?" (Journal of Finance 2023, open access, CC BY).
- Their data site (153 factors, 13 themes, 93 countries, India included): https://jkpfactors.com/
- Code: https://github.com/bkelly-lab/jkp-data (MIT; needs a WRDS subscription to rebuild)

## Kill methods (folder 03)
- ✅ Arnott, Harvey & Markowitz (2019), "A Backtesting Protocol in the Era of Machine Learning" (author copy, Duke).
- Gary Klein, "Performing a Project Premortem," HBR Sept 2007 (copyrighted, so linked): https://hbr.org/2007/09/performing-a-project-premortem · Klein's own page: https://www.gary-klein.com/premortem
- Free summary of the pre-mortem steps (Psychology Today, Klein): https://www.psychologytoday.com/us/blog/seeing-what-others-dont/202101/the-pre-mortem-method

## Videos and audio
- Daniel Kahneman on the pre-mortem (about 3 min): https://www.youtube.com/watch?v=f432ultnPQI
- Campbell Harvey, "The Risks of Historical Backtests" (JTPM 2015 talk): https://www.youtube.com/watch?v=aKehKmay4bY
- Excess Returns, "The Pitfalls of Backtesting": https://www.youtube.com/watch?v=tLsF8pvs6XY
- EconTalk podcast: Campbell Harvey on randomness, skill and investment strategies: https://www.econtalk.org/campbell-harvey-on-randomness-skill-and-investment-strategies/
- Harvey's practical one-pager on backtest haircuts: https://people.duke.edu/~charvey/Media/2016/Practical_applications_backtesting.pdf

## Already in earlier kits (re-read if needed)
Harvey–Liu–Zhu "…and the Cross-Section" and Harvey–Liu "Backtesting" (Day 5); McLean–Pontiff decay (Day 8); SEBI intraday study (Day 1).

## Build-along (folder 04), tested
- `card_killer.py` / `.ipynb` + `demo_cards.csv` + `verdicts_demo_cards.csv`; reuses Day 7's `nse_costs.py`.

## Templates (folder 05)
- `kill-session-protocol.md` (12 attacks + defence sheet), `premortem-template.md`, `backtest-protocol-checklist.md` (AHM 7 categories).
