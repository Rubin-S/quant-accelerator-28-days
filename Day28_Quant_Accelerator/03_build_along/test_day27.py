"""Day 27 tests. The two xfail tests are YOUR bugs for today: make them pass (they'll turn into XPASS → remove the marker)."""
import os, json, tempfile, pytest, pandas as pd
import drills, pipeline

@pytest.fixture(scope="module")
def results(): return {r.name.split()[0]: r for r in drills.run_all()}

@pytest.mark.parametrize("d", ["D01", "D02", "D03", "D04", "D06", "D07", "D08", "D09", "D10", "D11", "D12"])
def test_drill_safe(results, d):
    assert results[d].verdict == "PASS", results[d].observed

def test_d05_never_sends_twice(results):
    assert "broker orders 1" in results["D05"].observed           # safe today, for the wrong reason (see next test)

@pytest.mark.xfail(strict=True, reason="BUG-27-1: run_day ignores book['open_order_id'] set by recovery; relies on the duplicate-tag halt")
def test_d05_open_order_means_wait_not_halt(results):
    assert results["D05"].verdict == "PASS" and "halted=''" in results["D05"].observed

@pytest.mark.xfail(strict=True, reason="BUG-27-2: save_state leaves its temp file behind when the write fails")
def test_save_state_cleans_temp_on_failure(tmp_path, monkeypatch):
    p = tmp_path / "state.json"; pipeline.save_state(str(p), {"a": 1})
    def boom(*a, **k): raise OSError("disk full")
    monkeypatch.setattr(pipeline.json, "dump", boom)
    with pytest.raises(OSError): pipeline.save_state(str(p), {"a": 2})
    assert sorted(os.listdir(tmp_path)) == ["state.json"] and json.load(open(p)) == {"a": 1}

def test_drill_harness_detects_a_broken_kill_switch(monkeypatch):
    """Mutation check on the harness itself: if the kill file were ignored, D01 must FAIL."""
    import risk_engine
    real = risk_engine.os.path.exists
    monkeypatch.setattr(risk_engine.os.path, "exists", lambda p: False if str(p).endswith("KILL") else real(p))
    bars, sig = drills.load_data(); root = tempfile.mkdtemp()
    assert drills.d01_kill_file(bars, sig, root).verdict == "FAIL"
