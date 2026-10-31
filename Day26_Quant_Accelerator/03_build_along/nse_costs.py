"""
nse_costs.py: NSE cash-market cost calculator (equity shares and ETFs), Day 7 deliverable template.

EVERY rate below carries its source and the date it was checked. Rates change (they changed on
1 Oct 2024, 1 Mar 2026 and 1 Apr 2026). Re-check them before each use and bump RATES_AS_OF.

Scope: NSE cash market. Delivery (CNC) and intraday (MIS). Equity shares, equity ETFs (e.g. NIFTYBEES),
non-equity ETFs (e.g. GOLDBEES). No F&O: program rule.
"""
from dataclasses import dataclass, field

RATES_AS_OF = "2026-10-31"

@dataclass(frozen=True)
class Rates:
    # --- Statutory / exchange (same at every broker) ---
    # STT: Finance Act 2026 table, unchanged for cash equity from 1 Apr 2026 (NSE levies page; BSE master circular Apr 2026)
    stt_delivery_equity: float = 0.001        # 0.1% buy AND sell, equity shares
    stt_intraday_equity_sell: float = 0.00025 # 0.025% sell side only (non-delivery)
    stt_etf_equity_sell: float = 0.00001      # 0.001% sell side only, units of an equity-oriented fund, delivery
    stt_etf_equity_buy: float = 0.0           # NIL on purchase of equity-oriented fund units
    # NSE transaction charge incl. IPFT: Rs 306.99 + Rs 0.01 per crore each side from 1 Mar 2026 (NSE/FA/73061)
    nse_txn: float = 307 / 1e7                # = 0.00307%
    # SEBI turnover fee: Rs 10 per crore each side (NSE levies page)
    sebi_fee: float = 10 / 1e7
    # Stamp duty, buy side only (Indian Stamp Act as amended 2019, effective 1 Jul 2020; SEBI FAQ; NSE levies page)
    stamp_delivery_buy: float = 0.00015       # 0.015%
    stamp_intraday_buy: float = 0.00003       # 0.003%
    gst: float = 0.18                         # on brokerage + exchange txn + SEBI fee (not on STT or stamp duty)
    # --- Broker-specific: Zerodha published charges, checked 2026-10-31. EDIT for your broker. ---
    brokerage_delivery_pct: float = 0.0       # Rs 0 for equity delivery
    brokerage_intraday_pct: float = 0.0003    # 0.03% ...
    brokerage_intraday_cap: float = 20.0      # ... or Rs 20 per executed order, whichever is lower
    dp_charge_per_scrip_sell_day: float = 15.34  # Rs 3.5 CDSL + Rs 9.5 broker + Rs 2.34 GST, per scrip per day sold from demat
    round_stt_to_rupee: bool = True           # many contract notes round STT to the nearest rupee: VERIFY on yours

R = Rates()

def leg_costs(value, side, product="delivery", instrument="equity", rates=R):
    """Costs for ONE executed order (one leg). side 'buy'/'sell'. product 'delivery'/'intraday'.
    instrument 'equity' (shares), 'etf_equity' (e.g. NIFTYBEES), 'etf_other' (e.g. GOLDBEES, no STT).
    Returns a dict of rupee amounts (unrounded, except STT if round_stt_to_rupee)."""
    assert side in ("buy", "sell") and product in ("delivery", "intraday")
    assert instrument in ("equity", "etf_equity", "etf_other")
    c = {}
    # Brokerage
    if product == "delivery":
        c["brokerage"] = value * rates.brokerage_delivery_pct
    else:
        c["brokerage"] = min(value * rates.brokerage_intraday_pct, rates.brokerage_intraday_cap)
    # STT
    if instrument == "equity":
        stt = value * (rates.stt_delivery_equity if product == "delivery"
                       else (rates.stt_intraday_equity_sell if side == "sell" else 0.0))
    elif instrument == "etf_equity":
        if product == "delivery":
            stt = value * (rates.stt_etf_equity_sell if side == "sell" else rates.stt_etf_equity_buy)
        else:
            stt = value * (rates.stt_intraday_equity_sell if side == "sell" else 0.0)   # non-delivery sale of equity-fund units: 0.025%
    else:
        stt = 0.0
    c["stt"] = round(stt) if rates.round_stt_to_rupee else stt
    c["exchange_txn"] = value * rates.nse_txn
    c["sebi_fee"] = value * rates.sebi_fee
    c["stamp_duty"] = (value * (rates.stamp_delivery_buy if product == "delivery" else rates.stamp_intraday_buy)
                       if side == "buy" else 0.0)
    c["gst"] = rates.gst * (c["brokerage"] + c["exchange_txn"] + c["sebi_fee"])
    c["dp_charge"] = rates.dp_charge_per_scrip_sell_day if (side == "sell" and product == "delivery") else 0.0
    c["total"] = sum(v for k, v in c.items())
    return c

def round_trip(buy_value, sell_value, product="delivery", instrument="equity", rates=R):
    b = leg_costs(buy_value, "buy", product, instrument, rates)
    s = leg_costs(sell_value, "sell", product, instrument, rates)
    keys = [k for k in b if k != "total"]
    out = {k: b[k] + s[k] for k in keys}
    out["total"] = b["total"] + s["total"]
    out["bps_of_buy_value"] = out["total"] / buy_value * 1e4
    return out

def breakeven_move_pct(value, product="delivery", instrument="equity", rates=R):
    """Price move needed (in %) just to cover costs on a round trip of this size (ignoring spread)."""
    return round_trip(value, value, product, instrument, rates)["total"] / value * 100

def after_tax_gain(gain, holding_days, instrument="equity", ltcg_exempt_left=125000.0, cess=0.04):
    """Rough after-tax gain on ONE sale, resident individual, FY 2026-27 rates (unchanged by Budget 2026):
    listed equity / equity ETF: STCG 20% (<=12 months), LTCG 12.5% above Rs 1.25 lakh/yr (>12 months), +4% cess.
    Ignores surcharge, set-offs, slab income for etf_other. Not tax advice: a planning estimate."""
    if gain <= 0:
        return gain
    if instrument == "etf_other":
        raise ValueError("Non-equity ETFs: STCG at slab rate. Use your slab; not modelled here.")
    if holding_days <= 365:
        tax = gain * 0.20 * (1 + cess)
    else:
        tax = max(0.0, gain - ltcg_exempt_left) * 0.125 * (1 + cess)
    return gain - tax

def pretty(d):
    return "\n".join(f"  {k:18s} {v:10.2f}" for k, v in d.items())

if __name__ == "__main__":
    print(f"NSE cost calculator, rates as of {RATES_AS_OF}\n")
    for inst in ["equity", "etf_equity", "etf_other"]:
        print(f"Rs 1,00,000 DELIVERY round trip, {inst}:"); print(pretty(round_trip(1e5, 1e5, "delivery", inst)), "\n")
    print("Rs 1,00,000 INTRADAY round trip, equity:"); print(pretty(round_trip(1e5, 1e5, "intraday", "equity")), "\n")
    print("Breakeven move (round trip, % of value), NIFTYBEES delivery:")
    for v in [5_000, 25_000, 1_00_000, 5_00_000]:
        print(f"  Rs {v:>9,}: {breakeven_move_pct(v, 'delivery', 'etf_equity'):.3f}%")
    print("  Small trades pay far more in % terms: the Rs 15.34 DP charge is fixed per scrip per sell day.")
