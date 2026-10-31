"""
fire_drill.py: Day 24. Run on the VM BEFORE the first paper session. Each drill must end with an alert ON YOUR PHONE.
Tick each in session-1-log.md with the time the phone buzzed.

    python fire_drill.py            # sends 5 real test alerts through your configured channels
"""
from alerts import Alerter, redact
DRILLS = [
    ("CRIT", "DRILL 1: preflight failed (egress IP ≠ whitelisted) → no session"),
    ("CRIT", "DRILL 2: foreign order on NIFTYBEES (someone traded by hand) → HALT"),
    ("CRIT", "DRILL 3: position mismatch book 70 vs broker 0 → HALT"),
    ("WARN", "DRILL 4: KILL file present → no orders"),
    ("WARN", "DRILL 5: paper BUY 70 NIFTYBEES → COMPLETE (what a normal order alert looks like)"),
]
if __name__ == "__main__":
    a = Alerter.from_env(log_path="drill_alerts.log")
    for lvl, msg in DRILLS: print(lvl, msg, "→", a.send(lvl, msg) or "NOT DELIVERED (configure TELEGRAM_* or NTFY_URL)")
    print("Redaction check:", redact("access_token=abc123 api_secret: zzz"))
    print("Drill 6 (manual): stop the VM for 30 min tomorrow before the session window; healthchecks.io must email/alert you.")
