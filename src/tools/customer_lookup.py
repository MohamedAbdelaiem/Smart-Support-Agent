from langsmith import traceable
from src.database import get_session, list_all_customers, get_customer_by_name, customer_to_dict


def list_customers() -> list[dict]:
    """Backend/UI helper to return all active customers for UI dropdown selection."""
    session = get_session()
    try:
        customers = list_all_customers(session)
        return [customer_to_dict(c) for c in customers]
    finally:
        session.close()


@traceable(name="Lookup Customer Tool")
def lookup_customer(name: str) -> dict:
    """Looks up a customer's ID and details by name in PostgreSQL."""
    session = get_session()
    try:
        customer = get_customer_by_name(session, name)
        if not customer:
            return {"error": f"No customer found with name '{name}'"}
        return customer_to_dict(customer)
    finally:
        session.close()
