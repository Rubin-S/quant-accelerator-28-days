"""
preflight.py: Day 22. Run before any order, every morning. Each check returns (ok, detail). Any FAIL = no trading today.

    python preflight.py --static-ip 13.200.x.x --symbol NIFTYBEES

Checks:
  1. egress_ip     your server's public IP == the static IP whitelisted in the Kite developer console
                   (order APIs from any other IP are rejected; SEBI framework, live 1 Apr 2026)
  2. clock         server clock within 2 s of api.kite.trade's HTTP Date header (decision days and 06:00 expiry depend on it)
  3. timezone      the OS timezone is Asia/Kolkata (cron at "09:30" must mean IST)
  4. token         today's access token exists, is chmod 600 and unexpired
  5. profile       the token works: /user/profile answers, the CNC product + LIMIT order type are enabled, NSE is enabled
  6. funds         equity available cash >= the capital in rulebook.json
  7. instrument    the symbol exists in today's NSE instrument dump (and record its instrument_token)
  8. disk          >= 1 GB free for logs
"""
from __future__ import annotations
import argparse, datetime as dt, email.utils, json, os, shutil, sys, time, urllib.request
from kite_session import load_token, IST

def check_egress_ip(expected: str, fetch=None) -> tuple[bool, str]:
    fetch = fetch or (lambda: urllib.request.urlopen("https://checkip.amazonaws.com", timeout=10).read().decode().strip())
    ip = fetch(); return ip == expected, f"egress {ip} vs whitelisted {expected}"

def check_clock(fetch_date=None, max_skew_s: float = 2.0) -> tuple[bool, str]:
    def _f():
        r = urllib.request.urlopen(urllib.request.Request("https://api.kite.trade", method="HEAD"), timeout=10)
        return r.headers["Date"]
    try: hdr = (fetch_date or _f)()
    except Exception as e: return False, f"could not read server Date: {e}"
    remote = email.utils.parsedate_to_datetime(hdr).timestamp(); skew = time.time() - remote
    return abs(skew) <= max_skew_s, f"skew {skew:+.2f}s (max ±{max_skew_s}s; Date header has 1 s resolution)"

def check_timezone(tzname: str | None = None) -> tuple[bool, str]:
    tz = tzname or (open("/etc/timezone").read().strip() if os.path.exists("/etc/timezone") else
                    os.path.realpath("/etc/localtime").split("zoneinfo/")[-1])
    return tz in ("Asia/Kolkata", "Asia/Calcutta"), f"OS timezone {tz}"

def check_token(now=None, path=None) -> tuple[bool, str]:
    try: rec = load_token(now, path) if path else load_token(now)
    except PermissionError as e: return False, str(e)
    return (rec is not None), ("valid until " + rec["expires_at"]) if rec else "no valid token: run kite_session.py login"

def check_profile(kite) -> tuple[bool, str]:
    p = kite.profile(); miss = [x for x, s in (("NSE", p["exchanges"]), ("CNC", p["products"]), ("LIMIT", p["order_types"])) if x not in s]
    return not miss, f"user {p['user_id']}" + (f", missing {miss}" if miss else "")

def check_funds(kite, need_inr: float) -> tuple[bool, str]:
    cash = kite.margins("equity")["available"]["cash"]; return cash >= need_inr, f"available cash ₹{cash:,.0f} vs needed ₹{need_inr:,.0f}"

def check_instrument(kite, symbol: str) -> tuple[bool, str]:
    rows = [r for r in kite.instruments("NSE") if r["tradingsymbol"] == symbol]
    return bool(rows), (f"{symbol} instrument_token {rows[0]['instrument_token']} lot {rows[0].get('lot_size')}" if rows else f"{symbol} not found")

def check_disk(path: str = "/", min_gb: float = 1.0) -> tuple[bool, str]:
    free = shutil.disk_usage(path).free / 1e9; return free >= min_gb, f"{free:.1f} GB free"

def run(checks: dict) -> dict:
    out = {}
    for name, fn in checks.items():
        try: ok, detail = fn()
        except Exception as e: ok, detail = False, f"error: {e!r}"
        out[name] = dict(ok=bool(ok), detail=detail)
    out["ALL_OK"] = all(v["ok"] for v in out.values() if isinstance(v, dict))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--static-ip", required=True); ap.add_argument("--symbol", default="NIFTYBEES")
    ap.add_argument("--rulebook", default="rulebook.json"); ap.add_argument("--out", default="preflight.json")
    a = ap.parse_args()
    need = json.load(open(a.rulebook))["capital_at_risk_inr"] if os.path.exists(a.rulebook) else 0
    checks = dict(egress_ip=lambda: check_egress_ip(a.static_ip), clock=check_clock, timezone=check_timezone, token=check_token, disk=check_disk)
    rec = load_token()
    if rec:
        from kiteconnect import KiteConnect
        kite = KiteConnect(api_key=os.environ["KITE_API_KEY"]); kite.set_access_token(rec["access_token"])
        checks.update(profile=lambda: check_profile(kite), funds=lambda: check_funds(kite, need), instrument=lambda: check_instrument(kite, a.symbol))
    res = run(checks); res["ran_at"] = dt.datetime.now(IST).isoformat(timespec="seconds")
    json.dump(res, open(a.out, "w"), indent=1)
    for k, v in res.items():
        if isinstance(v, dict): print(f"{'PASS' if v['ok'] else 'FAIL'}  {k:11s} {v['detail']}")
    print("ALL OK: trading allowed today" if res["ALL_OK"] else "NOT OK: no orders today"); sys.exit(0 if res["ALL_OK"] else 1)

if __name__ == "__main__":
    main()
