"""
recovery.py: Day 24. On EVERY start: ask the broker what really happened today, then make your book agree or halt.

Knight Capital's lesson (Day 21): a system that trusts its own memory after a bad deploy or crash keeps sending orders.
Here the broker's order book (kite.orders(): today's orders only; it lives for a day) and holdings are the truth.

reconcile(broker_orders, book, our_prefix, broker_qty) returns (book, actions, halt_reason):
  * our order COMPLETE but not in the book          → apply the fill to the book (crash after send, before record)
  * our order OPEN / partially filled                 → leave it, record pending; never send a second one
  * our order REJECTED / CANCELLED                    → record the reason; the pipeline's attempt counter handles retry
  * an order NOT ours (no/foreign tag) on our symbol   → HALT: someone traded by hand or another app is live
  * after all that, book qty ≠ broker qty             → HALT
"""
from __future__ import annotations

TERMINAL = {"COMPLETE", "REJECTED", "CANCELLED"}

def reconcile(broker_orders: list[dict], book: dict, symbol: str, broker_qty: int, our_prefix: tuple = ("F10", "KILL")):
    actions, halt = [], ""
    seen = set(book.get("applied_order_ids", []))
    for o in broker_orders:
        if o.get("tradingsymbol") != symbol: continue
        tag = o.get("tag") or ""
        if not tag.startswith(our_prefix):
            halt = halt or f"foreign order {o['order_id']} on {symbol} (tag={tag!r})"; continue
        st = o["status"]
        if st == "COMPLETE" and o["order_id"] not in seen:
            sgn = 1 if o["transaction_type"] == "BUY" else -1
            book["qty"] += sgn * o["filled_quantity"]; book["cash"] -= sgn * o["filled_quantity"] * o["average_price"]
            seen.add(o["order_id"]); actions.append(f"applied missed fill {o['order_id']} {o['transaction_type']} {o['filled_quantity']} @ {o['average_price']}")
            if tag not in book.setdefault("tags", []): book["tags"].append(tag)
            book["pending_target"] = None
        elif st not in TERMINAL:
            book["open_order_id"] = o["order_id"]; actions.append(f"order {o['order_id']} still {st}: wait, do NOT resend")
            if tag not in book.setdefault("tags", []): book["tags"].append(tag)
        elif st in ("REJECTED", "CANCELLED"):
            actions.append(f"order {o['order_id']} {st}: {o.get('status_message') or ''}".strip())
            if tag not in book.setdefault("tags", []): book["tags"].append(tag)
    book["applied_order_ids"] = sorted(seen)
    if book["qty"] != broker_qty: halt = halt or f"position mismatch after recovery: book {book['qty']} vs broker {broker_qty}"
    return book, actions, halt
