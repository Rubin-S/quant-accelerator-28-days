# systemd units for Week 4 (paper sessions Mon 23, Wed 25, Thu 26, Fri 27 Nov)

/etc/systemd/system/trader-preflight.service
```
[Unit]
Description=Preflight checks
[Service]
Type=oneshot
User=trader
EnvironmentFile=/etc/rubin-trader/kite.env
WorkingDirectory=/home/trader/app
ExecStart=/home/trader/app/.venv/bin/python preflight.py --static-ip <YOUR_IP>
```
/etc/systemd/system/trader-preflight.timer
```
[Timer]
OnCalendar=Mon..Fri 09:20 Asia/Kolkata
Persistent=false
[Install]
WantedBy=timers.target
```
/etc/systemd/system/trader-run.service: same shape, `ExecStart=... python run_live.py --paper`, with `ExecCondition=` pointing at preflight.json ALL_OK.
/etc/systemd/system/trader-run.timer: `OnCalendar=Mon..Fri 15:00 Asia/Kolkata`

Rules: `Persistent=false` (a missed run must NOT fire late at 18:00 on reboot), holidays come from rulebook.json, never from systemd, and every unit logs to journald AND the JSONL journal.
