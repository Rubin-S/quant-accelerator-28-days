"""Day 20 code guards the one look. Test the guards."""
import json, math, os, subprocess, sys, numpy as np, pytest
from holdout_report import psr, expected_max_z
from seal_predictions import validate

def good():
    p = json.load(open(os.path.join(os.path.dirname(__file__), "demo", "predictions.json"))); return p

def test_demo_predictions_validate():
    assert validate(good()) == []

@pytest.mark.parametrize("breaker", [
    lambda p: p["oos_vol_ratio"].update(lo90=None),
    lambda p: p["oos_vol_ratio"].update(point=2.0),          # outside its own interval
    lambda p: p.update(p_dd_falsifier_passes=1.3),
    lambda p: p.update(dsr_n_trials=None),
    lambda p: p["falsifiers"].update(vol_ratio_max=None),
    lambda p: p.update(written_by=""),
])
def test_incomplete_predictions_rejected(breaker):
    p = good(); breaker(p); assert validate(p)

def test_expected_max_z():
    assert expected_max_z(1) == 0.0
    assert 1.5 < expected_max_z(10) < 1.6          # E[max of 10 std normals] ≈ 1.54
    assert expected_max_z(1000) > expected_max_z(100)

def test_psr_half_at_true_value_and_monotone():
    rng = np.random.default_rng(0); x = rng.normal(0.0005, 0.01, 5000)
    sr = x.mean() / x.std(ddof=1)
    assert psr(x, sr) == pytest.approx(0.5, abs=1e-9)
    assert psr(x, 0.0) > psr(x, 0.02)

def test_report_refuses_edited_predictions(tmp_path):
    d = tmp_path / "p"; d.mkdir(); pj = d / "predictions.json"; json.dump(good(), open(pj, "w"))
    here = os.path.dirname(os.path.abspath(__file__))
    subprocess.run([sys.executable, os.path.join(here, "seal_predictions.py"), "--demo", "--pred", str(pj)], check=True, capture_output=True)
    p = good(); p["oos_vol_ratio"]["point"] = 0.7; json.dump(p, open(pj, "w"))     # quiet edit after sealing
    r = subprocess.run([sys.executable, os.path.join(here, "holdout_report.py"), "--pred", str(pj), "--full-signal", "x", "--cash", "y",
                        "--out", str(tmp_path / "o")], capture_output=True, text=True)
    assert r.returncode != 0 and "changed after sealing" in (r.stderr + r.stdout)
