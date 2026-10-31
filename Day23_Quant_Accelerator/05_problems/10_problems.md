# Day 23: 10 problems
1. Parity says 0 mismatch days. Name two bugs it would catch and one it would NOT.
2. Why does the pipeline decide on day t but trade on t+1, when you could trade at 09:30 on t itself? What would changing it require?
3. The end-equity gap vs the engine is about −29 bps over 10 years. Where does it come from, and when would a gap be a red flag?
4. Marketable limits at the open filled 100% in the replay. Give two reasons that number is too optimistic for real NIFTYBEES.
5. Passive limits (−0.25%) missed 8 times and left the book out of sync for 7 days. Was the saving worth it? Do the arithmetic.
6. Why are order tags deterministic (date + side + attempt) instead of random UUIDs?
7. The state file is written to a temp file and then renamed. What failure does that prevent?
8. Your 15:00 run crashed after the order went out but before the fill was recorded. Walk through what the next run must do.
9. Why does a halt NOT clear itself in live mode, when the replay clears it every night?
10. List the four golden signals (SRE book) and give each one a concrete meaning for this pipeline.
