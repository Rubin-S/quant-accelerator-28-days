# Game day on the VM: Thu 26 Nov 2026 (PAPER only)
Rule: one fault at a time. Write the time you inject it and the time your PHONE buzzes. Undo it before the next one.
Do these BEFORE 09:15 or AFTER 15:30 IST, never while the session job is due to run.

| # | Fault (how) | Expected | Phone buzzed at | Recovered how | Pass? |
|---|---|---|---|---|---|
| G1 | `python kill.py halt "game day G1"` | KILL file, CRIT, `status` shows it; dashboard red | | `kill.py clear --note "…"` | |
| G2 | Run a session with the KILL file present | no order, WARN/CRIT | | | |
| G3 | `kill -9` the session process halfway (add a `sleep 30` before run_day on a copy) | heartbeat /fail or a missed ping → healthchecks alert; rerun is clean | | | |
| G4 | Lost connection: `sudo ufw deny out 443` then run preflight | preflight FAILS (egress/profile) → no session, CRIT | | `sudo ufw delete deny out 443` | |
| G5 | Expired token: log out of Kite web (kills the session), run preflight | TokenException → CRIT "re-login" | | manual login (Day 22) | |
| G6 | Wrong clock: `sudo timedatectl set-ntp false; sudo date -s "+5 min"` | preflight clock check fails | | `set-ntp true` | |
| G7 | Disk full: `fallocate -l <free−50MB> ~/fill.bin` | preflight disk check fails, or the state write fails safely | | `rm ~/fill.bin` | |
| G8 | Silent death: disable the cron line for one day | healthchecks.io alerts within the grace period | | re-enable | |

**Do NOT** test Zerodha's Console kill switch for fun: it locks the segment for 12 hours. Read the steps aloud instead (tabletop).

After: one blameless postmortem (Day 25 template) for anything that did NOT behave as expected.
