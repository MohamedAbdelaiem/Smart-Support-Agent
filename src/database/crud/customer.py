from uuid import UUID as PyUUID
from sqlalchemy.orm import Session
from src.database.models import Customer
from src.database.crud.base import parse_uuid


def get_customer_by_id(session: Session, customer_id: str | PyUUID) -> Customer | None:
    """Fetches a Customer from PostgreSQL by UUID or customer_id string."""
    cust_uuid = parse_uuid(customer_id)
    return session.get(Customer, cust_uuid)


def get_customer_by_name(session: Session, name: str) -> Customer | None:
    """Fetches a Customer by exact or case-insensitive name."""
    return session.query(Customer).filter(Customer.name.ilike(name.strip())).first()


def list_all_customers(session: Session) -> list[Customer]:
    """Fetches all customers from PostgreSQL ordered by name."""
    return session.query(Customer).order_by(Customer.name).all()


def customer_to_dict(customer: Customer) -> dict:
    """Serializes a Customer ORM instance into a clean dictionary."""
    return {
        "customer_id": str(customer.id),
        "name": customer.name,
    }


def create_customer(session: Session, name: str, customer_id: str | PyUUID | None = None) -> Customer:
    """Creates and persists a new Customer record in PostgreSQL."""
    cust_uuid = parse_uuid(customer_id) if customer_id else None
    customer = Customer(id=cust_uuid, name=name) if cust_uuid else Customer(name=name)
    session.add(customer)
    session.commit()
    return customer
