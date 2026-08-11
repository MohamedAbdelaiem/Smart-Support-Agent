import json
from pathlib import Path

# Path to mock_orders.json in root data/ directory
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
MOCK_ORDERS_FILE = DATA_DIR / "mock_orders.json"

LOOKUP_ORDER_SCHEMA = {
    "type": "object",
    "properties": {
        "order_id": {
            "type": "string",
            "description": "The unique order ID to look up (e.g. ORD-1001)",
        }
    },
    "required": ["order_id"],
    "additionalProperties": False,
}


def load_mock_orders() -> dict[str, dict]:
    """Loads mock orders indexed by order_id."""
    if not MOCK_ORDERS_FILE.exists():
        # Fallback dictionary if JSON file is missing
        return {
            "ORD-1001": {
                "order_id": "ORD-1001",
                "customer_name": "Alice Smith",
                "status": "delivered",
                "items": ["Wireless Headphones"],
                "total": 99.99,
            },
            "ORD-1002": {
                "order_id": "ORD-1002",
                "customer_name": "Bob Jones",
                "status": "shipped",
                "items": ["Mechanical Keyboard", "Mousepad"],
                "total": 149.50,
            },
        }

    with open(MOCK_ORDERS_FILE, "r", encoding="utf-8") as f:
        orders_list = json.load(f)
        return {order["order_id"]: order for order in orders_list}


def lookup_order(order_id: str) -> dict:
    """Looks up order details by order_id."""
    orders = load_mock_orders()
    if order_id not in orders:
        return {"error": f"No order found with id {order_id}"}
    return orders[order_id]
