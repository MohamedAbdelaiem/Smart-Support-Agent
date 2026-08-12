from src.tools.order_lookup import load_mock_orders



def refund_check(order_id: str, reason: str = "") -> dict:
    """Checks if an order is eligible for a refund."""
    orders = load_mock_orders()
    if order_id not in orders:
        return {"error": f"No order found with id {order_id}"}
    
    order = orders[order_id]
    status = order["status"]
    
    if status == "delivered":
        msg="Order is eligible for a refund."
        if reason:
            msg += f" Reason for refund request: {reason}"
        return {
            "refund_eligible": True,
            "refund_amount": order["total"],
            "status": status,
            "message": msg
        }
    elif status == "shipped":
        msg="Order is currently shipped and must be delivered before initiating a refund."
        if reason:
            msg += f" Reason for refund request: {reason}"
        return {
            "refund_eligible": False,
            "refund_amount": 0,
            "status": status,
            "message": msg
        }
    elif status == "refunded":
        msg="Order has already been refunded."
        if reason:
            msg += f" Reason for refund request: {reason}"
        return {
            "refund_eligible": False,
            "refund_amount": 0,
            "status": status,
            "message": msg
        }
    else:
        msg=f"Order status '{status}' is not eligible for a refund."
        if reason:
            msg += f" Reason for refund request: {reason}"
        return {
            "refund_eligible": False,
            "refund_amount": 0,
            "status": status,
            "message": msg
        }
