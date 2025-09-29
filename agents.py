# agents.py - simple mocked tools to demonstrate agentic capabilities
from typing import Dict

def price_lookup(sku: str) -> Dict:
    base = {"SKU123": 19.99, "SKU456": 5.49, "SKU789": 249.00}
    return {"sku": sku, "price": base.get(sku, 9.99)}

def inventory_check(store_id: str, sku: str) -> Dict:
    return {"store": store_id, "sku": sku, "qty": 7}

def issue_ticket(summary: str) -> Dict:
    return {"ticket_id": "INC-" + str(abs(hash(summary)) % 100000), "status": "OPEN"}
