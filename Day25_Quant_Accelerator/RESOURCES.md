# Day 25 resources: review, bug fixing, monitoring (checked 1 Nov 2026)

## Reviewing what went wrong, without lying to yourself
- Google SRE book, ch. 15 "Postmortem Culture: Learning from Failure": when to write one, blameless format, what goes in it. https://sre.google/sre-book/postmortem-culture/
- Google SRE workbook, "Postmortem Culture": a worked bad vs good postmortem, side by side. https://sre.google/workbook/postmortem-culture/
- John Allspaw (Etsy, 22 May 2012), "Blameless PostMortems and a Just Culture": the "second story": why the action made sense at the time. You are both the engineer and the manager here, so be honest without beating yourself up. https://www.etsy.com/codeascraft/blameless-postmortems

## Monitoring and alerting that you'll obey
- Google SRE book, ch. 10 "Practical Alerting": alert on symptoms, keep pages rare and actionable. https://sre.google/sre-book/practical-alerting/
- Google SRE workbook, "Alerting on SLOs": turning "is it healthy?" into numbers with thresholds. Your contract checks C1–C8 are a tiny version. https://sre.google/workbook/alerting-on-slos/
- SRE ch. 6 golden signals (Day 23 kit): the dashboard's middle panel.

## Measuring the order path
- Implementation shortfall: the gap between the paper decision and the real fill. The idea comes from André Perold, "The Implementation Shortfall: Paper Versus Reality", *Journal of Portfolio Management* 14(3), 1988 (paywalled, so no PDF here). `session_review.py` measures it per fill against the decision-day close.

## Build-along (03_build_along), 31 tests pass
- `session_review.py`: audits the journal against 8 session contracts (one EOD a day, no crash, every order resolved, blocked orders never sent, no unexplained mismatch, book = broker, every CRIT has an incident note, orders only after a decision or a labelled drill) + implementation shortfall table → `review.md`.
- `dashboard.py`: one static, read-only HTML page: status banner → risk headroom bars → golden signals → equity vs buy & hold (inline SVG) → preflight → alerts → journal tail. No JS, no CDN, served through an SSH tunnel.
- `demo_week.py`: a 9-session demo with a forced drill, a missing preflight and a planted mismatch, plus incident notes → `demo_out/review.md`, `demo_out/dashboard.html`. Open it in a browser first.
- Carried from Day 24: everything + tests.
