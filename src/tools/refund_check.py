from langsmith import traceable
from src.database import get_session, get_order_by_id, process_refund_order


@traceable(name="Refund Check Tool")
def refund_check(order_id: str, reason: str = "") -> dict:
    """Checks if an order is eligible for a refund using PostgreSQL database."""
    session = get_session()
    try:
        order = get_order_by_id(session, order_id)
        if not order:
            return {"error": f"No order found with id {order_id}"}

        status = order.status
        total_amount = order.total_amount

        if status == "delivered":
            msg = "Order is eligible for a refund."
            if reason:
                msg += f" Reason for refund request: {reason}"
            return {
                "refund_eligible": True,
                "refund_amount": total_amount,
                "status": status,
                "message": msg,
            }
        elif status == "shipped":
            msg = "Order is currently shipped and must be delivered before initiating a refund."
            if reason:
                msg += f" Reason for refund request: {reason}"
            return {
                "refund_eligible": False,
                "refund_amount": 0,
                "status": status,
                "message": msg,
            }
        elif status == "refunded":
            msg = "Order has already been refunded."
            if reason:
                msg += f" Reason for refund request: {reason}"
            return {
                "refund_eligible": False,
                "refund_amount": 0,
                "status": status,
                "message": msg,
                "refund_reason": order.refund_reason,
                "refund_amount_processed": order.refund_amount,
                "refunded_at": order.refunded_at.isoformat() if order.refunded_at else None,
            }
        else:
            msg = f"Order status '{status}' is not eligible for a refund."
            if reason:
                msg += f" Reason for refund request: {reason}"
            return {
                "refund_eligible": False,
                "refund_amount": 0,
                "status": status,
                "message": msg,
            }
    finally:
        session.close()


@traceable(name="Process Refund Tool")
def process_refund(order_id: str, customer_id: str = "", reason: str = "") -> dict:
    """Processes and executes a refund for an order in PostgreSQL with customer ownership verification."""
    session = get_session()
    try:
        return process_refund_order(
            session=session,
            order_id=order_id,
            customer_id=customer_id if customer_id else None,
            reason=reason,
        )
    finally:
        session.close()
