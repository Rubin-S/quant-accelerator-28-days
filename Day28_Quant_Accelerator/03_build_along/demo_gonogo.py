"""
demo_gonogo.py: Day 28 demo. Builds a full evidence pack from the Day 26 demo paper weeks and runs gonogo.py.

You'll see NO-GO, on purpose: the code in this folder still has the two Day 27 bugs (drill D05 is safe only by
accident), so G4 fails, and the demo memo sections are a stub, so G6 fails. Apply your Day 27 fixes and write
your own sections, and those gates flip. That's the point: the memo is decided by evidence, not by mood.
"""
import json, os, subprocess, sys
from risk_engine import load_rulebook
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "demo_out")
subprocess.run([sys.executable, os.path.join(HERE, "demo_paper_weeks.py")], check=True, capture_output=True)
_, rb_sha = load_rulebook(os.path.join(HERE, "rulebook.json"))
open(os.path.join(OUT, "replay_report.md"), "w").write("Day 23 replay: 0 mismatch days of 2522 (demo copy)\n")
open(os.path.join(OUT, "OPENED.log"), "w").write("2026-11-16T20:05 opened once (demo)\n")
open(os.path.join(OUT, "memo_sections.md"), "w").write("Thesis: TODO. What would make me stop: TODO.\n")
open(os.path.join(OUT, "incidents.md"), "w").write("")
alerts = [json.loads(l) for l in open(os.path.join(OUT, "alerts.log"))] if os.path.exists(os.path.join(OUT, "alerts.log")) else []
ev = dict(journal="journal.jsonl", state="state.json", alerts="alerts.log", incidents="incidents.md",
          bars="demo_ETF_bars.csv", signal="demo_NIFTY_signal.csv", rulebook="../rulebook.json", rulebook_locked_sha256=rb_sha,
          replay_mismatch_days=0, replay_report="replay_report.md", holdout_opened_log="OPENED.log",
          holdout_falsifiers_passed=True, game_day_passed=8, game_day_total=8,
          capital_at_risk_is_money_i_can_lose=True, memo_sections="memo_sections.md")
json.dump(ev, open(os.path.join(OUT, "evidence.json"), "w"), indent=2)
import gonogo
md = gonogo.to_md(gonogo.evaluate(ev, OUT)); open(os.path.join(OUT, "GO_NO_GO_demo.md"), "w").write(md); print(md)
