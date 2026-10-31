# VM runbook (fill in as you go; this is evidence for Day 28)

## Choice of box (pick one, write why)
| Option | Static IP | Cost notes (check your own account) |
|---|---|---|
| AWS EC2 in **ap-south-1 (Mumbai)** + Elastic IP | Elastic IP stays through stop/start | Every public IPv4 costs $0.005/hour since 1 Feb 2024 (~$3.65/month), in use or idle; 750 free hours/month only for accounts still in the 12-month EC2 free tier. Instance cost on top. |
| Any VPS with a dedicated IPv4 in India | Usually included | Check the IP is dedicated, not shared/NAT. |
| Home broadband | Rarely static | Don't. One ISP change = rejected orders. |

## Steps (tick + paste evidence)
- [ ] VM up: provider ___, region ___, OS Ubuntu 24.04, instance ___
- [ ] Static IP allocated + attached: ___ (screenshot)
- [ ] `sudo bash bootstrap_vm.sh <laptop ip>` ran clean (paste last 5 lines)
- [ ] SSH works with a key as `trader`; password login refused (paste the refusal)
- [ ] `timedatectl` shows Asia/Kolkata + NTP synchronized: yes
- [ ] Kite developer console: app created (Personal free, or Connect ₹500/month if you need live/historical data), redirect URL `http://127.0.0.1:5000/callback`
- [ ] Static IP added in the developer console profile (primary). Date ___
- [ ] `/etc/rubin-trader/kite.env` filled, mode 640 root:trader, NOT in git (`git check-ignore` proof)
- [ ] Laptop: `ssh -L 5000:127.0.0.1:5000 trader@<ip>` then `python kite_session.py login`: token saved, `status` OK
- [ ] `python preflight.py --static-ip <ip>` → ALL OK (attach preflight.json)
- [ ] Tomorrow 06:05 IST: `status` shows NO VALID TOKEN (proves expiry handling)

## Secrets rules
- api_secret only in kite.env on the VM. Never in code, git, chat, screenshots.
- If it ever leaks: regenerate it in the developer console the same hour.
