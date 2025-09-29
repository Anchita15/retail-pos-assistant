from datetime import datetime

_PRICES = {
    "SKU-1001": {"name": "Wireless Mouse", "price": 19.99, "currency": "USD"},
    "SKU-2002": {"name": "USB-C Cable 1m", "price": 7.49, "currency": "USD"},
}

_STOCK = {
    "SKU-1001": {"on_hand": 42, "store": "Store-01"},
    "SKU-2002": {"on_hand": 0, "store": "Store-01"},
}

def price_lookup(sku: str) -> dict:
    return _PRICES.get(sku, {"error": f"SKU {sku} not found"})

def inventory_check(sku: str) -> dict:
    return _STOCK.get(sku, {"error": f"No inventory for {sku}"})

def issue_ticket(title: str, detail: str) -> dict:
    return {
        "id": f"TKT-{int(datetime.utcnow().timestamp())}",
        "title": title,
        "detail": detail,
        "status": "OPEN",
    }
