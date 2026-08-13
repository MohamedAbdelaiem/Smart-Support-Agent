from langsmith import traceable
from src.database import get_session, get_order_by_id, order_to_dict


@traceable(name="Lookup Order Tool")
def lookup_order(order_id: str) -> dict:
    """Looks up order details by order_id from PostgreSQL database."""
    session = get_session()
    try:
        order = get_order_by_id(session, order_id)
        if not order:
            return {"error": f"No order found with id {order_id}"}
        return order_to_dict(order)
    finally:
        session.close()
