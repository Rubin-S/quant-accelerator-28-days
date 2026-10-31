"""No network, no real Kite: a fake client stands in. Every check must be able to FAIL."""
import datetime as dt, email.utils, json, os, time, pytest
from kite_session import login_url, checksum, expiry_for, save_token, load_token, parse_redirect, exchange, IST
import preflight as pf

def test_login_url_and_checksum():
    assert login_url("abc") == "https://kite.zerodha.com/connect/login?v=3&api_key=abc"
    import hashlib
    assert checksum("k", "r", "s") == hashlib.sha256(b"krs").hexdigest()

@pytest.mark.parametrize("login,exp", [
    (dt.datetime(2026, 11, 21, 8, 50, tzinfo=IST), dt.datetime(2026, 11, 22, 6, 0, tzinfo=IST)),
    (dt.datetime(2026, 11, 21, 23, 59, tzinfo=IST), dt.datetime(2026, 11, 22, 6, 0, tzinfo=IST)),
    (dt.datetime(2026, 11, 21, 5, 30, tzinfo=IST), dt.datetime(2026, 11, 21, 6, 0, tzinfo=IST))])
def test_expiry(login, exp):
    assert expiry_for(login) == exp

def test_token_roundtrip_private_and_expiry(tmp_path):
    p = str(tmp_path / "t.json"); login = dt.datetime(2026, 11, 21, 8, 50, tzinfo=IST)
    save_token("AT", "AB1234", login, p)
    assert oct(os.stat(p).st_mode & 0o777) == "0o600"
    assert load_token(login + dt.timedelta(hours=3), p)["access_token"] == "AT"
    assert load_token(dt.datetime(2026, 11, 22, 6, 1, tzinfo=IST), p) is None
    os.chmod(p, 0o644)
    with pytest.raises(PermissionError): load_token(login, p)

def test_parse_redirect():
    assert parse_redirect("/callback?action=login&type=login&status=success&request_token=RT1") == "RT1"
    with pytest.raises(ValueError): parse_redirect("/callback?status=cancelled")

class FakeKite:
    def __init__(self, cash=50000, symbols=("NIFTYBEES",), products=("CNC", "MIS")):
        self.cash, self.symbols, self.products = cash, symbols, products
    def generate_session(self, rt, api_secret): return dict(access_token="AT-" + rt, user_id="AB1234", login_time=dt.datetime(2026, 11, 21, 8, 50))
    def profile(self): return dict(user_id="AB1234", exchanges=["NSE", "BSE"], products=list(self.products), order_types=["MARKET", "LIMIT"])
    def margins(self, seg): return dict(available=dict(cash=self.cash))
    def instruments(self, ex): return [dict(tradingsymbol=s, instrument_token=2707457, lot_size=1) for s in self.symbols]

def test_exchange_saves(tmp_path, monkeypatch):
    import kite_session
    p = str(tmp_path / "t.json")
    real = kite_session.save_token
    monkeypatch.setattr(kite_session, "save_token", lambda at, uid, lt: real(at, uid, lt, p))
    r = kite_session.exchange(FakeKite(), "RT9", "secret")
    assert r["access_token"] == "AT-RT9" and r["expires_at"].startswith("2026-11-22T06:00")

def test_preflight_checks_can_fail():
    assert pf.check_egress_ip("1.2.3.4", fetch=lambda: "1.2.3.4")[0]
    assert not pf.check_egress_ip("1.2.3.4", fetch=lambda: "5.6.7.8")[0]
    now_hdr = email.utils.formatdate(time.time(), usegmt=True); old_hdr = email.utils.formatdate(time.time() - 30, usegmt=True)
    assert pf.check_clock(lambda: now_hdr)[0] and not pf.check_clock(lambda: old_hdr)[0]
    assert pf.check_timezone("Asia/Kolkata")[0] and not pf.check_timezone("UTC")[0]
    assert pf.check_profile(FakeKite())[0] and not pf.check_profile(FakeKite(products=("MIS",)))[0]
    assert pf.check_funds(FakeKite(cash=50000), 20000)[0] and not pf.check_funds(FakeKite(cash=100), 20000)[0]
    assert pf.check_instrument(FakeKite(), "NIFTYBEES")[0] and not pf.check_instrument(FakeKite(symbols=()), "NIFTYBEES")[0]

def test_run_marks_exceptions_as_fail():
    res = pf.run(dict(a=lambda: (True, "ok"), b=lambda: 1 / 0))
    assert res["a"]["ok"] and not res["b"]["ok"] and not res["ALL_OK"]
