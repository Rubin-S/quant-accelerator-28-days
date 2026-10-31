# Solutions
1. If the signal differs, positions will too; if positions differ, fills are on different days and can't be compared. Check upstream first. *Diff causes before effects.*
2. (a) Data revision: the close you saw live changed later (check the raw file hashes from Day 13); (b) code drift: live and backtest run different code (re-run parity, Day 23). Same data plus a different answer means code. *Pin the data, then blame the code.*
3. That fills, fees and books are recorded and computed correctly end to end, not market slippage. *Paper tests plumbing, not prices.*
4. Positive: NIFTYBEES tracks the TRI (dividends reinvested, ~1.2% yield on 30 Sep 2026) minus a 0.04% expense ratio, while the backtest uses the price index; the daily premium noise averages out. *Know which index your instrument tracks.*
5. n ≈ (2·8/5)² ≈ 10.2, so 11 fills; at ~2 trades a year that's about 5–6 years. *Some questions only time can answer.*
6. "Slippage: assumption 5 bps; measured on n = 1–2 fills, which can't decide; I'll treat it as unverified, keep the size small, and re-test after 11 real fills." *State the uncertainty, don't hide it.*
7. Money left the books that no line explains: a missed fee, a fill recorded at the wrong price or quantity, cash interest, or a corporate action. Find it before trusting anything else. *Books that don't add up are a bug.*
8. Their trader is huge, institutional, trades thousands of stocks with algorithms in developed markets; your cost is mostly the bid-ask spread and fixed charges on a tiny ticket in one Indian ETF. *Borrow methods, not numbers.*
9. In "timing_and_sizing" as a small cash drag; ~1% of exposure is noise next to tracking and slippage, but it must be explainable. *Explain small gaps so you notice big ones.*
10. Stop when D1 or D2 has an unexplained mismatch, or the D5 residual is above 5 bps; log (don't stop) for slippage or tracking within known bands. *Logic errors stop the system; noise gets logged.*
