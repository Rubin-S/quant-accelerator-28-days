"""
gonogo.py: Day 28. Gather every piece of evidence from four weeks, check it against the graduation gates, and write
the skeleton of your go/no-go memo. The tool can say NO-GO on its own. It can never say GO on its own: the
human sections must be written, and even a full pass only unlocks STAGE 1 (tiny real money).

    python gonogo.py --evidence evidence.json --out GO_NO_GO.md

evidence.json (paths are relative to this folder; see 04_templates/evidence_example.json):
  journal, state, alerts, incidents        paper week artefacts (Day 24–27)
  bars, signal                             NIFTYBEES bars + NIFTY closes for the same days (Day 26)
  rulebook, rulebook_locked_sha256         Day 21 lock: the file you trade must be the file you locked
  replay_mismatch_days, replay_report      Day 23 parity: the number AND the file it came from
  holdout_opened_log                       Day 20 OPENED.log (must show ≤ 1 run)
  holdout_falsifiers_passed                true/false/null: your Day 20 pre-registered falsifiers on the holdout
  game_day_passed, game_day_total          Day 27 VM game day rows passed (phone buzz time written)
  capital_at_risk_is_money_i_can_lose      true/false: you answer this, nobody else
  memo_sections                            path to your written sections (thesis, what would make me stop, etc.)

Gates (all must PASS for GO STAGE 1):
  G0 Strategy       holdout falsifiers passed (the plumbing can't rescue a strategy that failed its own test)
  G1 No unexplained orders      session review C3/C5/C8 + live-vs-backtest D2
  G2 Signal parity              replay 0 mismatch days + every live decision recomputes the same (D1)
  G3 Slippage                   live_vs_backtest verdict WITHIN; UNDECIDED = PASS WITH CAVEAT (stated in the memo)
  G4 Failure drills             drills.py 12/12 PASS (no SAFE-BUT-ACCIDENTAL) + every game-day row passed
  G5 Integrity                  rulebook hash = locked; holdout opened at most once
  G6 Human                      capital is money you can lose; memo sections written
"""
from __future__ import annotations
import argparse, hashlib, json, math, os
import numpy as np, pandas as pd
import session_review as sr, live_vs_backtest as lvb, drills
from pipeline import faber_signal

HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda base, p: p if (p is None or os.path.isabs(p)) else os.path.join(base, p)

def sha(path): return hashlib.sha256(open(path, "rb").read()).hexdigest()

# ------------------------------------------------------------------ Minimum Track Record Length (Bailey & López de Prado 2012)
def min_trl(returns: pd.Series, sr_star: float = 0.0, alpha: float = 0.05) -> float:
    """Observations needed before a measured Sharpe ratio beats sr_star with (1-alpha) confidence.
    MinTRL = 1 + [1 − γ3·SR + (γ4 − 1)/4·SR²] · (Z_α / (SR − SR*))²   (SR, SR* per period; γ4 = raw kurtosis)."""
    from statistics import NormalDist
    x = returns.dropna(); s = x.mean() / x.std(ddof=1)
    if s <= sr_star: return math.inf
    g3 = float(((x - x.mean()) ** 3).mean() / x.std(ddof=0) ** 3); g4 = float(((x - x.mean()) ** 4).mean() / x.std(ddof=0) ** 4)
    z = NormalDist().inv_cdf(1 - alpha)
    return 1 + (1 - g3 * s + (g4 - 1) / 4 * s ** 2) * (z / (s - sr_star)) ** 2

def strategy_monthly_returns(signal: pd.Series, months: int = 10) -> pd.Series:
    """Rough in/out Faber monthly returns on the INDEX (no costs, no cash yield): only to size MinTRL, never to judge."""
    m = signal.resample("ME").last().dropna(); r = m.pct_change()
    pos = pd.Series([faber_signal(m.iloc[:k + 1], months) or 0 for k in range(len(m))], m.index).shift(1)
    return (pos * r).dropna().iloc[months:]

# ------------------------------------------------------------------ gates
def evaluate(ev: dict, base: str, run_drills=drills.run_all) -> dict:
    g = {}
    j = sr.load_jsonl(P(base, ev["journal"])); st = json.load(open(P(base, ev["state"]))) if ev.get("state") and os.path.exists(P(base, ev["state"])) else None
    al = sr.load_jsonl(P(base, ev.get("alerts"))); inc = open(P(base, ev["incidents"])).read() if ev.get("incidents") and os.path.exists(P(base, ev["incidents"])) else ""
    rv = sr.review(j, st, al, inc)
    bars = pd.read_csv(P(base, ev["bars"]), parse_dates=["Date"], index_col="Date"); sig = pd.read_csv(P(base, ev["signal"]), parse_dates=["Date"], index_col="Date")["Close"]
    df = lvb.diff(j, bars, sig)

    v = ev.get("holdout_falsifiers_passed")
    g["G0 Strategy"] = ("PASS" if v is True else "FAIL" if v is False else "MISSING", f"holdout falsifiers passed = {v}")

    bad = [a for a in rv["anomalies"] if any(c in a for c in ("C3", "C5", "C8"))]
    unexpl_pos = [m for m in df["d2_mismatch_days"] if m not in df["d2_explained_by_drill"]]
    g["G1 No unexplained orders"] = ("PASS" if not bad and not unexpl_pos else "FAIL",
                                     f"{len(bad)} order anomalies, {len(unexpl_pos)} unexplained position days, {len(rv['anomalies'])} anomalies of any kind")

    rm = ev.get("replay_mismatch_days"); rp = ev.get("replay_report")
    d1_bad = [x for x in df["d1"] if not x["match"]]
    if rm is None or not (rp and os.path.exists(P(base, rp))): g["G2 Signal parity"] = ("MISSING", "replay number or its report file missing")
    else: g["G2 Signal parity"] = ("PASS" if rm == 0 and not d1_bad else "FAIL",
                                   f"replay {rm} mismatch days; live decisions {len(df['d1'])}, mismatched {len(d1_bad)}" + (" (none in window: D1 untested live)" if not df["d1"] else ""))

    s = df["slip"]
    g["G3 Slippage"] = ({"WITHIN": "PASS", "OUTSIDE": "FAIL"}.get(s["verdict"].split()[0], "PASS WITH CAVEAT"),
                        f"verdict {s['verdict']}, n = {s['n']} fills" + (f", ≈{s['n_needed']} fills needed to decide" if s.get("n_needed") else ""))

    res = run_drills(); n_pass = sum(r.verdict == "PASS" for r in res)
    gd, gt = ev.get("game_day_passed"), ev.get("game_day_total", 8)
    g["G4 Failure drills"] = ("PASS" if n_pass == len(res) and gd == gt else "FAIL",
                              f"code drills {n_pass}/{len(res)} PASS" + "".join(f"; {r.name.split()[0]} {r.verdict}" for r in res if r.verdict != "PASS") + f"; game day {gd}/{gt}")

    rb = P(base, ev["rulebook"]); now_sha = sha(rb); locked = ev.get("rulebook_locked_sha256")
    opened = open(P(base, ev["holdout_opened_log"])).read().strip().count("\n") + 1 if ev.get("holdout_opened_log") and os.path.exists(P(base, ev["holdout_opened_log"])) and open(P(base, ev["holdout_opened_log"])).read().strip() else 0
    ok5 = locked == now_sha and opened <= 1
    g["G5 Integrity"] = ("PASS" if ok5 else "FAIL", f"rulebook sha {now_sha[:12]}… {'=' if locked == now_sha else '≠'} locked {str(locked)[:12]}…; holdout opened {opened}×")

    memo = P(base, ev.get("memo_sections")); words = len(open(memo).read().split()) if memo and os.path.exists(memo) else 0
    ok6 = ev.get("capital_at_risk_is_money_i_can_lose") is True and words >= 300
    g["G6 Human"] = ("PASS" if ok6 else "FAIL", f"money I can lose = {ev.get('capital_at_risk_is_money_i_can_lose')}; memo sections {words} words (≥ 300)")

    trl_m = min_trl(strategy_monthly_returns(sig.loc[:"2018-12-31"])) if len(sig) > 300 else math.nan
    states = [x[0] for x in g.values()]
    verdict = "NO-GO" if any(x in ("FAIL", "MISSING") for x in states) else "GO: STAGE 1 ONLY"
    return dict(gates=g, verdict=verdict, review=rv, diff=df, min_trl_months=trl_m, drills=res)

def to_md(r: dict) -> str:
    L = ["# Go / no-go memo: graduation, Fri 27 Nov 2026", "", f"## Verdict: **{r['verdict']}**", "",
         "| Gate | Result | Evidence |", "|---|---|---|"]
    L += [f"| {k} | **{v[0]}** | {v[1]} |" for k, v in r["gates"].items()]
    t = r["min_trl_months"]
    L += ["", "## How long until live results mean anything",
          f"Minimum track record length (Bailey & López de Prado 2012) to show this rule's in-sample Sharpe is above 0 at 95%: "
          + (f"**≈ {t:.0f} months (~{t/12:.0f} years)** of live monthly returns." if math.isfinite(t) else "**infinite**: the in-sample Sharpe isn't above 0.")
          + " Until then, live P&L is noise: judge the system on plumbing and rule adherence, never on returns.",
          "", "## What GO means (and doesn't)",
          "- GO = Stage 1 of the ramp plan only (04_templates/ramp_plan.md). Never the full capital on day one.",
          "- GO is a statement about the PLUMBING and your DISCIPLINE, not proof of edge. This rule is a drawdown/volatility overlay with no alpha claim (Day 11).",
          "- NO-GO is a good outcome if the evidence says so. The paper week continues; nothing is lost but time.",
          "", "## Sections only you can write (memo_sections file)",
          "1. Thesis in two sentences, and what it is NOT.  2. What would make me stop (numbers).  3. Pre-mortem: it's 1 Jun 2027 and this failed, why?  "
          "4. The money: amount, and why losing all of it changes nothing in my life.  5. Who checks me (a mentor, a friend, this log)."]
    return "\n".join(L)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--evidence", required=True); ap.add_argument("--out", default="GO_NO_GO.md")
    a = ap.parse_args(); ev = json.load(open(a.evidence)); base = os.path.dirname(os.path.abspath(a.evidence))
    md = to_md(evaluate(ev, base)); open(a.out, "w").write(md); print(md)

if __name__ == "__main__":
    main()
