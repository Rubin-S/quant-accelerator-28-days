# Solutions
1. No order you can't explain; book qty = broker qty; every CRIT reaches your phone within minutes (plus: one EOD line per session). *Safe = measurable.*
2. D04: nothing reached the exchange, so a retry is correct. D05: the exchange has the order but you don't know, so a blind retry doubles the position (the Knight pattern). *The danger is not knowing, not the failure.*
3. The duplicate-tag guard is a last line of defence; leaning on it turns a normal wait into a HALT and a page every time the network blips, and a future tag change could remove the protection silently. *Design safety in; don't inherit it by luck.*
4. A test that can't fail proves nothing (Day 16 mutation testing). *Test the tester.*
5. The cause (margin, holdings, band) needs a human to read it; resizing and resending turns one error into an order-storm risk, and the max-rejects rule exists for this. *A rejection is a message: read it.*
6. Known: you sent it. Unknown: whether it reached the exchange. Next call: orders() and look for your tag (recovery.reconcile), never place_order again. *Ask the broker before you act.*
7. Your phone and alert channels, cron and healthchecks, the firewall and static IP, the clock, the disk, the real Kite login and token expiry, and your own reaction time with the runbook. *Code drills test logic; game days test the system and you.*
8. The runbook lives in a repo you won't open at 09:25 while panicking; your phone has no saved SSH command; nobody else knows how to run `kill.py`. Fix: a pinned note on your phone with the 3 commands. *If you can't find the plan, there is no plan.*
9. It locks the segment for 12 hours and needs no open orders or positions; testing it costs a trading day and proves only Zerodha's button. *Don't drill what you can't undo cheaply.*
10. "drills.py: 12/12 PASS, 0 SAFE-BUT-ACCIDENTAL; game day G1–G8 each with a phone-buzz time ≤ 5 min and a written recovery; every surprise has a postmortem." *A pass you can check, not a feeling.*

## BUG fixes (open only after writing yours)
```diff
--- 03_build_along/pipeline.py	2026-10-31 19:50:27.254256152 +0000
+++ /tmp/fxr/03_build_along/pipeline.py	2026-10-31 19:51:24.760000000 +0000
@@ -116,8 +116,12 @@
 
 def save_state(path: str, d: dict):
     fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(path)) or ".")
-    with os.fdopen(fd, "w") as f: json.dump(d, f, default=str)
-    os.replace(tmp, path)                      # atomic: a crash mid-write never leaves half a state file
+    try:
+        with os.fdopen(fd, "w") as f: json.dump(d, f, default=str)
+        os.replace(tmp, path)
+    except BaseException:
+        if os.path.exists(tmp): os.remove(tmp)
+        raise                      # atomic: a crash mid-write never leaves half a state file
 
 # ------------------------------------------------------------------ one trading day
 def run_day(today: pd.Timestamp, hist: pd.DataFrame, book: dict, broker, rb: dict, journal: Journal,
@@ -132,6 +136,8 @@
 
     # 1. execute yesterday's decision today (Day 15 timing: decide on t, trade on t+1)
     tgt = book.get("pending_target")
+    if tgt is not None and book.get("open_order_id"):
+        journal.log("wait", date=today, why=f"order {book['open_order_id']} still open at broker: do not resend"); tgt = None
     if tgt is not None:
         ref = bar.Close if order_time >= "15:00" else bar.Open           # the LTP we'd see when sending (no peeking at the close at 09:30)
         equity_est = book["cash"] + book["qty"] * ref
--- 03_build_along/recovery.py	2026-10-31 19:50:27.262886418 +0000
+++ /tmp/fxr/03_build_along/recovery.py	2026-10-31 19:51:24.760000000 +0000
@@ -17,7 +17,7 @@
 
 def reconcile(broker_orders: list[dict], book: dict, symbol: str, broker_qty: int, our_prefix: tuple = ("F10", "KILL")):
     actions, halt = [], ""
-    seen = set(book.get("applied_order_ids", []))
+    seen = set(book.get("applied_order_ids", [])); book["open_order_id"] = None
     for o in broker_orders:
         if o.get("tradingsymbol") != symbol: continue
         tag = o.get("tag") or ""
```
