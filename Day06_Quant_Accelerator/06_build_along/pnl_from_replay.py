"""Compute the naive market maker's P&L from YOUR orderbook_replay output.
Usage: python3 pnl_from_replay.py replay_out.txt naive_mm_session_truth.csv
TRADE lines are: TRADE,bid_id,ask_id,price_ticks,qty. MM ids are >= 1,000,000."""
import sys, pandas as pd
MM = 1_000_000; TICK = 0.01
cash = 0.0; inv = 0; n = 0
for line in open(sys.argv[1]):
    p = line.strip().split(",")
    if p[0] != "TRADE": continue
    bid, ask, px, q = int(p[1]), int(p[2]), int(p[3]) * TICK, int(p[4])
    if bid >= MM: cash -= px * q; inv += q; n += 1      # MM bought
    if ask >= MM: cash += px * q; inv -= q; n += 1      # MM sold
final_V = pd.read_csv(sys.argv[2]).true_value.iloc[-1]
print(f"MM fills: {n}; final inventory {inv}; P&L marked to true value {cash + inv*final_V:+.2f}")
