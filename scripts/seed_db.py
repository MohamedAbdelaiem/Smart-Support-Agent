import json
import uuid
from datetime import datetime
from pathlib import Path
from uuid import UUID as PyUUID

from src.database import Customer, Order, create_tables, get_session

# Path to mock_orders.json
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MOCK_ORDERS_FILE = DATA_DIR / "mock_orders.json"


def parse_uuid(val: str) -> PyUUID:
    """Parses a string into a UUID, generating a deterministic UUID if not in standard format."""
    try:
        return PyUUID(val)
    except (ValueError, TypeError):
        # Generate a deterministic UUID v5 from arbitrary string (e.g. 'ORD-1001')
        return uuid.uuid5(uuid.NAMESPACE_DNS, val)


def parse_datetime(val: str | None) -> datetime | None:
    """Parses an ISO format datetime string if provided."""
    if not val:
        return None
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    except ValueError:
        return None


def seed_database() -> None:
    """Seeds PostgreSQL database tables with initial customer and order data."""
    if not MOCK_ORDERS_FILE.exists():
        print(f"Error: Mock orders file not found at {MOCK_ORDERS_FILE}")
        return

    print("Initializing database tables...")
    create_tables()

    session = get_session()
    try:
        with open(MOCK_ORDERS_FILE, "r", encoding="utf-8") as f:
            raw_orders = json.load(f)

        customers_created = 0
        orders_created = 0

        for item in raw_orders:
            cust_uuid = parse_uuid(item.get("customer_id", item["customer_name"]))
            cust_name = item["customer_name"]

            # Check if customer already exists
            customer = session.get(Customer, cust_uuid)
            if not customer:
                customer = Customer(id=cust_uuid, name=cust_name)
                session.add(customer)
                session.flush()
                customers_created += 1

            # Parse order details
            order_uuid = parse_uuid(item["order_id"])

            # Check if order already exists
            existing_order = session.get(Order, order_uuid)
            if not existing_order:
                new_order = Order(
                    id=order_uuid,
                    customer_id=customer.id,
                    status=item.get("status", "processing"),
                    total_amount=float(item.get("total", 0.0)),
                    delivery_date=parse_datetime(item.get("delivery_date")),
                    items=item.get("items", []),
                    refund_reason=item.get("refund_reason"),
                    refund_amount=float(item["refund_amount"]) if item.get("refund_amount") is not None else None,
                    refunded_at=parse_datetime(item.get("refunded_at")),
                )
                session.add(new_order)
                orders_created += 1

        session.commit()
        print("Seeding completed successfully!")
        print(f"   - Customers created: {customers_created}")
        print(f"   - Orders created: {orders_created}")

    except Exception as e:
        session.rollback()
        print(f"Error during database seeding: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
