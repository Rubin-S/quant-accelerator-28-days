"""
Daily drill: MAKE A MARKET (5 minutes, play 5 rounds)
I hide a random quantity. You quote a bid and an ask (spread no wider than the limit).
I then trade against you at whichever side is better for me, using the TRUE value.
Your score is how much you made. Narrow, accurate quotes win; wide or lazy quotes lose.

Run: python make_a_market.py
"""
import random

GAMES = [
    ("sum of 3 dice", lambda: sum(random.randint(1, 6) for _ in range(3)), 10.5, 2.0),
    ("max of 2 dice", lambda: max(random.randint(1, 6), random.randint(1, 6)), 161/36, 1.0),
    ("number of heads in 10 flips", lambda: sum(random.random() < 0.5 for _ in range(10)), 5.0, 1.5),
    ("product of 2 dice", lambda: random.randint(1, 6) * random.randint(1, 6), 12.25, 3.0),
    ("min of 3 dice", lambda: min(random.randint(1, 6) for _ in range(3)), 2.042, 1.0),
]
total = 0.0
for name, draw, fair, max_spread in random.sample(GAMES, 5):
    print(f"\nMake a market on: {name}.  Max spread {max_spread}.")
    while True:
        try:
            bid, ask = map(float, input("  bid ask > ").split())
            if ask < bid or ask - bid > max_spread + 1e-9: raise ValueError
            break
        except ValueError:
            print(f"  need two numbers, bid <= ask, spread <= {max_spread}")
    outcome = draw()
    # Counterparty is 'informed' about the fair value: buys from you if fair > ask, sells to you if fair < bid.
    if fair > ask:   pnl, side = ask - outcome, "I BOUGHT from you at your ask"
    elif fair < bid: pnl, side = outcome - bid, "I SOLD to you at your bid"
    else:            pnl, side = 0.0, "No trade: your quote straddled fair value. Good."
    total += pnl
    print(f"  {side}. Fair value {fair:.2f}, outcome {outcome}. Your P&L this round: {pnl:+.2f}")
print(f"\nTotal P&L: {total:+.2f}.  Log it. Aim: quotes that always straddle fair value, as tight as you can compute.")
