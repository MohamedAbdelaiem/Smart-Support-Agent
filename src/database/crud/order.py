from datetime import datetime
from uuid import UUID as PyUUID
from sqlalchemy.orm import Session
from src.database.models import Order
from src.database.crud.base import parse_uuid


def get_order_by_id(session: Session, order_id: str | PyUUID) -> Order | None:
    """Fetches an Order from PostgreSQL by UUID or order_id string."""
    order_uuid = parse_uuid(order_id)
    return session.get(Order, order_uuid)


def get_orders_by_customer_id(session: Session, customer_id: str | PyUUID) -> list[Order]:
    """Fetches all orders belonging to a specific customer_id."""
    cust_uuid = parse_uuid(customer_id)
    return session.query(Order).filter(Order.customer_id == cust_uuid).all()


def create_order(
    session: Session,
    customer_id: str | PyUUID,
    total_amount: float,
    items: list[str],
    status: str = "processing",
    delivery_date: datetime | None = None,
    order_id: str | PyUUID | None = None,
) -> Order:
    """Creates and persists a new Order record in PostgreSQL."""
    cust_uuid = parse_uuid(customer_id)
    ord_uuid = parse_uuid(order_id) if order_id else None

    order_kwargs = {
        "customer_id": cust_uuid,
        "total_amount": total_amount,
        "items": items,
        "status": status,
        "delivery_date": delivery_date,
    }
    if ord_uuid:
        order_kwargs["id"] = ord_uuid

    order = Order(**order_kwargs)
    session.add(order)
    session.commit()
    return order


def process_refund_order(
    session: Session,
    order_id: str | PyUUID,
    customer_id: str | PyUUID | None = None,
    reason: str = "",
) -> dict:
    """
    Validates order eligibility and optional customer ownership, then updates order status to 'refunded'.
    """
    order = get_order_by_id(session, order_id)
    if not order:
        return {"error": f"No order found with id {order_id}"}

    # Customer Ownership Check
    if customer_id:
        cust_uuid = parse_uuid(customer_id)
        if order.customer_id != cust_uuid:
            return {"error": f"Unauthorized: Order {order_id} does not belong to customer {customer_id}"}

    if order.status == "refunded":
        return {
            "error": "Order has already been refunded.",
            "status": order.status,
            "refund_reason": order.refund_reason,
            "refund_amount": order.refund_amount,
            "refunded_at": order.refunded_at.isoformat() if order.refunded_at else None,
        }

    if order.status != "delivered":
        return {
            "error": f"Order status '{order.status}' is not eligible for a refund. Order must be delivered first.",
            "status": order.status,
        }

    # Perform refund update
    now = datetime.utcnow()
    order.status = "refunded"
    order.refund_reason = reason or "Customer requested refund"
    order.refund_amount = order.total_amount
    order.refunded_at = now
    session.commit()

    return {
        "success": True,
        "order_id": str(order.id),
        "customer_id": str(order.customer_id),
        "status": order.status,
        "refund_amount": order.refund_amount,
        "refund_reason": order.refund_reason,
        "refunded_at": order.refunded_at.isoformat() if order.refunded_at else None,
        "message": f"Order {order_id} has been successfully refunded ${order.total_amount:.2f}.",
    }


def order_to_dict(order: Order) -> dict:
    """Serializes an Order ORM instance into a clean dictionary."""
    return {
        "order_id": str(order.id),
        "customer_id": str(order.customer_id),
        "customer_name": order.customer.name if order.customer else "Unknown",
        "status": order.status,
        "items": order.items or [],
        "total": order.total_amount,
        "delivery_date": order.delivery_date.isoformat() if order.delivery_date else None,
        "refund_reason": order.refund_reason,
        "refund_amount": order.refund_amount,
        "refunded_at": order.refunded_at.isoformat() if order.refunded_at else None,
    }
