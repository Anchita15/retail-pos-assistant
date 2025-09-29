# agents.py — simple mocked tools for demo
from datetime import datetime

def price_lookup(sku: str):
    sku = (sku or "").strip().upper()
    if not sku:
        return {"ok": False, "error": "Missing SKU"}
    price_map = {
        "SKU123": 19.99,
        "SKU456": 7.49,
        "SKU789": 129.00,
    }
    price = price_map.get(sku, 14.95)  # default demo price
    return {
        "ok": True,
        "sku": sku,
        "price": price,
        "currency": "USD",
        "source": "demo-catalog",
        "at": datetime.utcnow().isoformat() + "Z",
    }

def inventory_check(store_id: str, sku: str):
    store_id = (store_id or "").strip().upper()
    sku = (sku or "").strip().upper()
    if not store_id or not sku:
        return {"ok": False, "error": "Missing store_id or sku"}
    stock = 42 if sku.endswith("6") else 12
    return {
        "ok": True,
        "store_id": store_id,
        "sku": sku,
        "on_hand": stock,
        "on_order": 8,
        "safety_stock": 3,
        "source": "demo-inventory",
        "at": datetime.utcnow().isoformat() + "Z",
    }

def issue_ticket(summary: str):
    summary = (summary or "").strip()
    if not summary:
        return {"ok": False, "error": "Missing summary"}
    return {
        "ok": True,
        "ticket_id": "INC-" + datetime.utcnow().strftime("%Y%m%d%H%M%S"),
        "summary": summary,
        "status": "OPEN",
        "priority": "P3",
        "assignee": "POS-Support-Queue",
    }
