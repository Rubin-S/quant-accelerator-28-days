# First live day: one page (from SRE Appendix E, cut to what has bitten traders before)
Every line answers a question backed by a known disaster (Knight 2012, Day 21; your own drills, Day 27).

**The day before**
- [ ] gonogo.py = GO: STAGE 1 ONLY, memo signed and dated, sent to the person who checks you
- [ ] Kite Connect plan active; static IP registered (≤ 2), 2FA on, API key's redirect URL correct (Day 22)
- [ ] Funds in the account = Stage 1 size + fees margin, NOT more (the account balance is a risk limit too)
- [ ] rulebook.json hash = locked; capital_at_risk set to the Stage 1 size (that's an amendment: did you wait 48 h?)
- [ ] Code: the exact git commit that passed drills 12/12 and parity. Tag it `live-v1`. No other code on the VM.
- [ ] Broker switch: PaperBroker → KiteBroker is ONE config line; a test proves the paper path is unchanged
- [ ] Holidays list for 2026 and 2027 filled (rulebook says FILL)

**Live day**
- [ ] Manual login (no TOTP bots), preflight ALL_OK, dashboard green, phone on and loud
- [ ] Watch the first order in the Kite app as it happens: tag, LIMIT, CNC, quantity, price
- [ ] After the fill: recovery reconciles, book = broker, journal has a fill line, alert reached the phone
- [ ] Evening: session_review + live_vs_backtest + a training-log row. Nothing is changed in code tonight.

**Abort criteria (any = kill.py halt and go back to paper)**
- an order you can't explain · a quantity or price you didn't expect · book ≠ broker after recovery · no alert on your phone
