# pyrefly: ignore [missing-import]
from src.tools.order_lookup import load_mock_orders

REFUND_CHECK_SCHEMA = {
    "type": "object",
    "properties": {
        "order_id": {
            "type": "string",
            "description": "The order ID to check refund eligibility for, e.g., 'ORD-1001'",
        },
        "reason": {
            "type": "string",
            "description": "Brief explanation for why the refund is being requested",
        },
    },
    "required": ["order_id"],
    "additionalProperties": False,
}

def refund_check(order_id: str, reason: str = "") -> dict:
    """Checks if an order is eligible for a refund."""
    orders = load_mock_orders()
    if order_id not in orders:
        return {"error": f"No order found with id {order_id}"}
    
    order = orders[order_id]
    status = order["status"]
    
    if status == "delivered":
        return {
            "refund_eligible": True,
            "refund_amount": order["total"],
            "status": status,
            "message": "Order is eligible for a refund."
        }
    elif status == "shipped":
        return {
            "refund_eligible": False,
            "refund_amount": 0,
            "status": status,
            "message": "Order is currently shipped and must be delivered before initiating a refund."
        }
    elif status == "refunded":
        return {
            "refund_eligible": False,
            "refund_amount": 0,
            "status": status,
            "message": "Order has already been refunded."
        }
    else:
        return {
            "refund_eligible": False,
            "refund_amount": 0,
            "status": status,
            "message": f"Order status '{status}' is not eligible for a refund."
        }
