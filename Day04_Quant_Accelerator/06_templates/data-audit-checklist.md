# Data audit checklist v0 (run on EVERY dataset before any analysis)
Start it today; it becomes your Day 13–14 audit.

- [ ] Source, download date, and exact symbols written down
- [ ] Date range and row count; compare against the exchange's trading calendar (NSE holidays)
- [ ] NaNs: where, how many, what I did with them
- [ ] Duplicate dates
- [ ] Moves bigger than X% that reverse the next day (bad ticks, wrong split adjustment)
- [ ] Corporate actions: splits, bonuses, dividends: is the series adjusted? Price index or total return?
- [ ] Time zone and the exact time each value becomes known (close at 15:30 IST? US close = next morning IST)
- [ ] Survivorship: does this universe include things that died? (Index/ETF: mostly safe)
- [ ] Plot it. Look at it with your eyes.
