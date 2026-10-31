"""GATE 1 check: is your calculator within 20% of a real contract note?
1. Get one real contract note (your own trade; or, if you have no account yet, a trade priced on your
   broker's official brokerage calculator page, saved as a screenshot).
2. Fill NOTE below with the numbers exactly as printed. 3. Run: python3 contract_note_check.py
DP charges are NOT on a Zerodha contract note (they're in the funds statement), so they're excluded here."""
from nse_costs import leg_costs

NOTE = {  # <-- EDIT: one scrip, one day
    "buy_value": 0.0, "sell_value": 0.0, "product": "delivery", "instrument": "etf_equity",
    "printed": {"brokerage": 0.0, "stt": 0.0, "exchange_txn": 0.0, "sebi_fee": 0.0, "stamp_duty": 0.0, "gst": 0.0},
}

def main(n=NOTE):
    calc = {k: 0.0 for k in n["printed"]}
    for side, val in (("buy", n["buy_value"]), ("sell", n["sell_value"])):
        if val > 0:
            c = leg_costs(val, side, n["product"], n["instrument"])
            for k in calc: calc[k] += c[k]
    tot_p, tot_c = sum(n["printed"].values()), sum(calc.values())
    if tot_p == 0:
        print("Fill NOTE with your contract note numbers first."); return
    print(f"{'item':14s} {'note':>10s} {'mine':>10s} {'diff %':>8s}")
    for k in calc:
        p, c = n["printed"][k], calc[k]
        d = (c - p) / p * 100 if p else float('nan')
        print(f"{k:14s} {p:10.2f} {c:10.2f} {d:8.1f}")
    err = (tot_c - tot_p) / tot_p * 100
    print(f"{'TOTAL':14s} {tot_p:10.2f} {tot_c:10.2f} {err:8.1f}")
    print("GATE 1 cost check:", "PASS" if abs(err) <= 20 else "FAIL", "(|error| <= 20%). Explain every line that differs, even if you pass.")

if __name__ == "__main__":
    main()
