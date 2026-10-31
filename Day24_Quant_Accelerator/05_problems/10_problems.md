# Day 24: 10 problems
1. Why does HALT keep the position while KILL flattens it? Give one situation where flattening on a HALT would hurt you.
2. Zerodha's Console kill switch needs no open orders first and locks you out for 12 hours. Why is it layer 3 and not layer 1?
3. Your process crashed right after `place_order` returned an order_id. On restart the order is OPEN at the broker. What must happen, and what must NOT?
4. Why does a foreign order (no F10 tag) halt the system even if it's on the right side?
5. Why is a heartbeat from OUTSIDE the VM needed when you already send alerts from inside it?
6. WARN alerts are deduped for 30 minutes but CRIT never is. Defend both choices.
7. Paper week (23–27 Nov) has no decision day: the next is Tue 1 Dec. What does the paper week prove, what can't it prove, and why use `--force-target` only once?
8. ntfy topics are public to anyone who knows the name. What may and may not go in an alert?
9. The kill flatten uses a −1% LIMIT, not a market order. What can go wrong with that, and what's your fallback?
10. Write the single sentence you'll put in incidents.md if you ever trade by hand in the Kite app during Week 4.
