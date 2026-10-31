# Build-along: who_pays_whom.py
A 100-line market with informed traders, noise traders and a market maker (Treynor 1971 / Glosten-Milgrom 1985),
plus a Monte Carlo of zero-edge traders paying costs, set against SEBI's intraday numbers.

Run (after setup):  uv run python who_pays_whom.py
Or plain:           pip install numpy matplotlib && python3 who_pays_whom.py

Expected with default knobs:
- informed ~ +32,000, noise ~ -32,000, market maker ~ 0 (it sets the break-even spread)
- zero-edge traders: ~69% lose at 100 trades/yr, ~87% at 500 trades/yr

Before EACH change to the knobs, write your prediction in the training log. Then run.
The 4 questions are at the bottom of the script. who_pays_whom.png is the reference chart.
