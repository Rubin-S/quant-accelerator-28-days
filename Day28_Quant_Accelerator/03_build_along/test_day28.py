import json, math, os, shutil, subprocess, sys, tempfile
import numpy as np, pandas as pd, pytest
import gonogo, drills

HERE = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture(scope="module")
def demo():
    subprocess.run([sys.executable, os.path.join(HERE, "demo_gonogo.py")], check=True, capture_output=True)
    out = os.path.join(HERE, "demo_out"); return json.load(open(os.path.join(out, "evidence.json"))), out

def all_pass(): return [drills.Result(f"D{i:02d} x", "", "", "PASS") for i in range(1, 13)]

def test_demo_is_no_go_for_the_right_reasons(demo):
    ev, out = demo; r = gonogo.evaluate(ev, out)
    assert r["verdict"] == "NO-GO" and r["gates"]["G4 Failure drills"][0] == "FAIL" and r["gates"]["G6 Human"][0] == "FAIL"

def test_never_full_go_only_stage1(demo, tmp_path):
    ev, out = demo; ev = dict(ev); m = tmp_path / "m.md"; m.write_text("word " * 320); ev["memo_sections"] = str(m)
    r = gonogo.evaluate(ev, out, run_drills=all_pass)
    assert r["verdict"] == "GO: STAGE 1 ONLY"

@pytest.mark.parametrize("key,val,gate", [("holdout_falsifiers_passed", False, "G0 Strategy"), ("holdout_falsifiers_passed", None, "G0 Strategy"),
                                         ("replay_mismatch_days", 3, "G2 Signal parity"), ("rulebook_locked_sha256", "0" * 64, "G5 Integrity"),
                                         ("game_day_passed", 7, "G4 Failure drills"), ("capital_at_risk_is_money_i_can_lose", False, "G6 Human")])
def test_each_gate_can_veto(demo, tmp_path, key, val, gate):
    ev, out = demo; ev = dict(ev); m = tmp_path / "m.md"; m.write_text("word " * 320); ev["memo_sections"] = str(m); ev[key] = val
    r = gonogo.evaluate(ev, out, run_drills=all_pass)
    assert r["verdict"] == "NO-GO" and r["gates"][gate][0] in ("FAIL", "MISSING")

def test_holdout_opened_twice_fails(demo, tmp_path):
    ev, out = demo; ev = dict(ev); m = tmp_path / "m.md"; m.write_text("word " * 320); ev["memo_sections"] = str(m)
    log = tmp_path / "OPENED.log"; log.write_text("run 1\nrun 2\n"); ev["holdout_opened_log"] = str(log)
    assert gonogo.evaluate(ev, out, run_drills=all_pass)["gates"]["G5 Integrity"][0] == "FAIL"

def test_min_trl_matches_formula():
    rng = np.random.default_rng(0); x = pd.Series(rng.normal(0.01, 0.04, 5000))      # SR 0.25 per period, ~normal
    t = gonogo.min_trl(x); s = x.mean() / x.std(ddof=1)
    approx = 1 + (1 + s ** 2 / 2) * (1.6449 / s) ** 2                               # normal: γ3=0, γ4=3
    assert abs(t / approx - 1) < 0.05 and gonogo.min_trl(-x) == math.inf
