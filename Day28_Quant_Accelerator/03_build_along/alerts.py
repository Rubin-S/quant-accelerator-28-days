"""
alerts.py: Day 24. Phone alerts that you'll actually read.

Channels (pick one or both; both are free):
  * Telegram bot: create with @BotFather, put TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID in /etc/rubin-trader/kite.env.
    Sends via the Bot API method sendMessage (https://core.telegram.org/bots/api#sendmessage).
  * ntfy: POST plain text to https://ntfy.sh/<your-long-random-topic> and subscribe in the ntfy app (https://docs.ntfy.sh/publish/).
    Anyone who guesses the topic can read it, so use a long random topic and never put money amounts you'd mind leaking.

Rules built in:
  * Three levels. INFO goes to the log only; WARN and CRIT go to the phone. CRIT ignores dedupe.
  * The same WARN within 30 minutes is sent once (alert fatigue kills alerting).
  * Never send secrets: anything that looks like a token/secret is redacted before it leaves the box.
  * Sending must never crash the trading process: failures are logged and swallowed.
"""
from __future__ import annotations
import datetime as dt, json, os, re, time, urllib.parse, urllib.request
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))

LEVELS = {"INFO": 0, "WARN": 1, "CRIT": 2}
SECRET_RE = re.compile(r"(access_token|api_secret|api_key|token|secret)\s*[=:]\s*\S+", re.I)

def redact(text: str) -> str:
    return SECRET_RE.sub(lambda m: m.group(1) + "=<redacted>", text)

def _post(url: str, data: bytes, headers: dict | None = None, timeout: float = 10) -> int:
    req = urllib.request.Request(url, data=data, headers=headers or {}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r: return r.status

class Alerter:
    def __init__(self, telegram_token=None, telegram_chat=None, ntfy_url=None, log_path="alerts.log",
                 dedupe_s: int = 1800, post=_post, clock=time.time):
        self.tg_token, self.tg_chat, self.ntfy = telegram_token, telegram_chat, ntfy_url
        self.log_path, self.dedupe_s, self.post, self.clock = log_path, dedupe_s, post, clock
        self._last: dict[str, float] = {}

    @classmethod
    def from_env(cls, **kw):
        return cls(os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID"), os.environ.get("NTFY_URL"), **kw)

    def send(self, level: str, text: str) -> list[str]:
        """Returns the channels it actually delivered to (for tests and the session log)."""
        assert level in LEVELS
        text = redact(f"[{level}] {text}")
        with open(self.log_path, "a") as f: f.write(json.dumps(dict(ts=dt.datetime.now(IST).isoformat(timespec="seconds"), level=level, text=text)) + "\n")
        if LEVELS[level] < LEVELS["WARN"]: return []
        now = self.clock()
        if level == "WARN" and now - self._last.get(text, -1e18) < self.dedupe_s: return []
        self._last[text] = now; sent = []
        if self.tg_token and self.tg_chat:
            try:
                body = urllib.parse.urlencode(dict(chat_id=self.tg_chat, text=text)).encode()
                self.post(f"https://api.telegram.org/bot{self.tg_token}/sendMessage", body); sent.append("telegram")
            except Exception as e: self._fail("telegram", e)
        if self.ntfy:
            try:
                self.post(self.ntfy, text.encode(), {"Priority": "urgent" if level == "CRIT" else "default", "Title": "trader " + level}); sent.append("ntfy")
            except Exception as e: self._fail("ntfy", e)
        return sent

    def _fail(self, ch, e):
        with open(self.log_path, "a") as f: f.write(json.dumps(dict(ts=dt.datetime.now(IST).isoformat(timespec="seconds"), level="ERROR", text=f"{ch} send failed: {e!r}")) + "\n")

class Heartbeat:
    """Dead man's switch. healthchecks.io (free Hobbyist plan: 20 checks) alerts YOU when a ping does NOT arrive on schedule.
    Ping URLs: https://hc-ping.com/<uuid>  (+ /start, /fail). This catches what in-process alerts can't: the VM is dead."""
    def __init__(self, url: str | None, post=_post): self.url, self.post = url, post
    def _ping(self, suffix=""):
        if not self.url: return False
        try: self.post(self.url + suffix, b""); return True
        except Exception: return False
    def start(self): return self._ping("/start")
    def ok(self): return self._ping("")
    def fail(self): return self._ping("/fail")
