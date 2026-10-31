"""
kite_session.py: Day 22. The daily Kite Connect login, done the way the rules allow.

Facts this file is built on (checked 1 Nov 2026):
  * Login: open https://kite.zerodha.com/connect/login?v=3&api_key=... , log in by hand (password + TOTP), Kite redirects
    to YOUR registered redirect URL with ?request_token=... . POST request_token + checksum = SHA-256(api_key +
    request_token + api_secret) to /session/token → access_token. (kite.trade/docs/connect/v3/user)
  * request_token lives "only a few minutes"; access_token expires at 06:00 the next day (regulatory). Same docs.
  * Zerodha: "As per exchange requirement, users must log in manually at least once each day … we do not recommend
    automating the login." (Kite forum, 2025–2026). So: NO TOTP bots here. One human login a day, one command.
  * api_secret never leaves the server; never in git; never in a browser.

How the redirect reaches a VM with no web server: register http://127.0.0.1:5000/callback as the redirect URL, then on
your laptop run   ssh -L 5000:127.0.0.1:5000 trader@<static-ip>   and open the login URL in your laptop browser.
Kite redirects your browser to 127.0.0.1:5000, the SSH tunnel carries it to the VM, this script catches it.

    python kite_session.py login      # prints the URL, waits for the redirect, saves the token (chmod 600)
    python kite_session.py status     # is today's token present and unexpired?
"""
from __future__ import annotations
import datetime as dt, hashlib, json, os, stat, sys, urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
TOKEN_PATH = os.environ.get("KITE_TOKEN_PATH", os.path.expanduser("~/.kite/token.json"))

def login_url(api_key: str) -> str:
    return f"https://kite.zerodha.com/connect/login?v=3&api_key={urllib.parse.quote(api_key)}"

def checksum(api_key: str, request_token: str, api_secret: str) -> str:
    return hashlib.sha256((api_key + request_token + api_secret).encode()).hexdigest()

def expiry_for(login_time: dt.datetime) -> dt.datetime:
    """Token dies at 06:00 IST on the day after login (a 05:30 login still dies at 06:00 the SAME morning? No: the docs say
    'next day'. We take the conservative reading: the first 06:00 IST strictly after login)."""
    t = login_time.astimezone(IST)
    six = t.replace(hour=6, minute=0, second=0, microsecond=0)
    return six if t < six else six + dt.timedelta(days=1)

def save_token(access_token: str, user_id: str, login_time: dt.datetime, path: str = TOKEN_PATH) -> dict:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rec = dict(access_token=access_token, user_id=user_id, login_time=login_time.isoformat(),
               expires_at=expiry_for(login_time).isoformat())
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f: json.dump(rec, f)
    os.chmod(path, 0o600)
    return rec

def load_token(now: dt.datetime | None = None, path: str = TOKEN_PATH) -> dict | None:
    """Returns the token record only if it exists, is private (0600) and is unexpired. Otherwise None."""
    if not os.path.exists(path): return None
    if stat.S_IMODE(os.stat(path).st_mode) & 0o077: raise PermissionError(f"{path} is readable by others: chmod 600 it")
    rec = json.load(open(path)); now = now or dt.datetime.now(IST)
    return rec if now < dt.datetime.fromisoformat(rec["expires_at"]) else None

def parse_redirect(path: str) -> str:
    q = urllib.parse.parse_qs(urllib.parse.urlparse(path).query)
    if q.get("status", [""])[0] != "success" or "request_token" not in q: raise ValueError(f"login did not succeed: {q}")
    return q["request_token"][0]

def exchange(kite, request_token: str, api_secret: str) -> dict:
    """kite = kiteconnect.KiteConnect(api_key). generate_session computes the same checksum internally."""
    data = kite.generate_session(request_token, api_secret=api_secret)
    lt = data.get("login_time")
    login_time = lt if isinstance(lt, dt.datetime) else dt.datetime.now(IST)
    if login_time.tzinfo is None: login_time = login_time.replace(tzinfo=IST)
    return save_token(data["access_token"], data.get("user_id", "?"), login_time)

def _catch_one_redirect(port: int = 5000) -> str:
    box = {}
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            try: box["rt"] = parse_redirect(self.path); msg = b"Logged in. You can close this tab."
            except Exception as e: box["err"] = str(e); msg = b"Login failed. Check the terminal."
            self.send_response(200); self.end_headers(); self.wfile.write(msg)
        def log_message(self, *a): pass
    srv = HTTPServer(("127.0.0.1", port), H)        # localhost only: reachable through your SSH tunnel, not the internet
    srv.timeout = 300; srv.handle_request()
    if "rt" not in box: sys.exit(box.get("err", "no redirect within 5 minutes"))
    return box["rt"]

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        rec = load_token(); print("NO VALID TOKEN: run `login`" if not rec else f"OK {rec['user_id']} until {rec['expires_at']}"); return
    if cmd == "login":
        from kiteconnect import KiteConnect           # pip install kiteconnect (pin a version that has market_protection)
        key, secret = os.environ["KITE_API_KEY"], os.environ["KITE_API_SECRET"]
        print("Open on your laptop (SSH tunnel up):\n ", login_url(key))
        rt = _catch_one_redirect(int(os.environ.get("KITE_CALLBACK_PORT", 5000)))
        rec = exchange(KiteConnect(api_key=key), rt, secret)
        print(f"Token saved for {rec['user_id']}, valid until {rec['expires_at']}")

if __name__ == "__main__":
    main()
