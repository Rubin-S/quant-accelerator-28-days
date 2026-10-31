"""
seal_predictions.py: Day 20, step 1. Run this BEFORE you see a single 2019+ number.

    python seal_predictions.py --prereg ../my/preregistration.md --lock ../my/LOCK.txt --pred ../04_templates/predictions.json

It checks that:
  1. your pre-registration still matches its locked SHA-256 (no quiet edits since Day 12),
  2. every prediction has a point AND a 90% interval, every probability is in [0, 1], and the DSR trial count is filled in,
then writes PREDICTIONS_LOCK.txt (sha256 of predictions + pre-reg, UTC timestamp) and prints the holdout password.

Honest note: you could read the password out of this file. Nothing stops a cheat except the log. holdout_report.py
refuses to run if predictions.json changed after sealing, and writes every opening to OPENED.log. Grading is on the log.
"""
import argparse, base64, datetime as dt, hashlib, json, os, sys

REQ_INTERVALS = ["oos_sharpe_xs_strategy", "oos_sharpe_xs_buyhold", "oos_vol_ratio", "oos_dd_edge_pp", "oos_max_dd_strategy_pct",
                 "oos_n_round_trips"]
REQ_PROBS = ["p_vol_falsifier_passes", "p_dd_falsifier_passes", "p_strategy_sharpe_beats_buyhold"]
_K = "T09TLU9OQ0UtMTkxMQ=="

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()

def validate(pred):
    errs = []
    for k in REQ_INTERVALS:
        v = pred.get(k, {})
        if not all(isinstance(v.get(x), (int, float)) for x in ("point", "lo90", "hi90")): errs.append(f"{k}: need point, lo90, hi90 as numbers")
        elif not v["lo90"] <= v["point"] <= v["hi90"]: errs.append(f"{k}: need lo90 <= point <= hi90")
    for k in REQ_PROBS:
        v = pred.get(k)
        if not isinstance(v, (int, float)) or not 0 <= v <= 1: errs.append(f"{k}: need a probability in [0, 1]")
    f = pred.get("falsifiers", {})
    for k in ("vol_ratio_max", "dd_edge_min_pp"):
        if not isinstance(f.get(k), (int, float)): errs.append(f"falsifiers.{k}: copy it EXACTLY from your locked pre-reg")
    for k in ("dsr_n_trials", "dsr_trial_sharpe_std_annual"):
        if not isinstance(pred.get(k), (int, float)) or pred.get(k) <= 0: errs.append(f"{k}: decided on Day 17, needed now")
    if not str(pred.get("written_by", "")).strip(): errs.append("written_by: your name")
    return errs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prereg"); ap.add_argument("--lock"); ap.add_argument("--pred", required=True)
    ap.add_argument("--demo", action="store_true", help="skip the pre-reg check (kit demo only)")
    a = ap.parse_args()
    if not a.demo:
        if not (a.prereg and a.lock): sys.exit("STOP: give --prereg and --lock (or --demo for the kit's example)")
        h = sha(a.prereg)
        if h not in open(a.lock).read(): sys.exit(f"STOP: pre-reg sha256 {h[:12]}... not in {a.lock}. It changed after locking.")
    pred = json.load(open(a.pred)); errs = validate(pred)
    if errs: sys.exit("STOP: predictions incomplete:\n  - " + "\n  - ".join(errs))
    out = os.path.join(os.path.dirname(os.path.abspath(a.pred)), "PREDICTIONS_LOCK.txt")
    if os.path.exists(out): sys.exit(f"STOP: {out} already exists. Predictions are sealed once. Delete it only if you haven't opened the holdout, and say so in the log.")
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    open(out, "w").write(f"predictions_sha256 {sha(a.pred)}\nprereg_sha256 {sha(a.prereg) if a.prereg else 'DEMO'}\nsealed_utc {now}\n")
    print(f"Sealed: {out}\nHoldout password: {base64.b64decode(_K).decode()}\n"
          "Unzip 06_data/SEALED_holdout_2019_2026.zip, then run holdout_report.py ONCE. Every run is logged.")

if __name__ == "__main__":
    main()
