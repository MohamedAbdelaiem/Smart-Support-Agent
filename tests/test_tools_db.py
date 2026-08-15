import uuid
from src.tools.order_lookup import lookup_order
from src.tools.refund_check import refund_check, process_refund
from src.tools.customer_lookup import list_customers
from src.database import get_session, create_order, get_customer_by_name


def test_list_customers():
    """Tests fetching list of available customers."""
    customers = list_customers()
    assert isinstance(customers, list)
    assert len(customers) >= 7
    customer_names = [c["name"] for c in customers]
    assert "Alice Smith" in customer_names
    assert "Bob Jones" in customer_names


def test_lookup_order_success():
    """Tests looking up an existing order from PostgreSQL."""
    result = lookup_order("ORD-1001")
    assert "error" not in result
    assert result["status"] == "delivered"
    assert result["customer_name"] == "Alice Smith"
    assert result["total"] == 99.99


def test_lookup_order_not_found():
    """Tests looking up a non-existent order."""
    result = lookup_order("ORD-9999")
    assert "error" in result
    assert "No order found" in result["error"]


def test_refund_check_eligible():
    """Tests refund check for a delivered order."""
    result = refund_check("ORD-1001", reason="Item damaged")
    assert result["refund_eligible"] is True
    assert result["refund_amount"] == 99.99
    assert result["status"] == "delivered"
    assert "Item damaged" in result["message"]


def test_process_refund_unauthorized_customer():
    """Tests processing refund fails if customer_id does not match order owner."""
    session = get_session()
    try:
        alice = get_customer_by_name(session, "Alice Smith")
        bob = get_customer_by_name(session, "Bob Jones")
        assert alice is not None
        assert bob is not None

        # Attempt to refund Alice's order ORD-1001 using Bob's customer_id
        res = process_refund(order_id="ORD-1001", customer_id=str(bob.id), reason="Fraud attempt")
        assert "error" in res
        assert "Unauthorized" in res["error"]
    finally:
        session.close()


def test_process_refund_success():
    """Tests executing a refund for a delivered order with matching customer_id."""
    session = get_session()
    try:
        alice = get_customer_by_name(session, "Alice Smith")
        assert alice is not None

        # Generate a unique order_id for each test run to avoid unique constraint violations
        unique_order_id = f"ORD-TEST-{uuid.uuid4().hex[:8]}"

        new_order = create_order(
            session=session,
            customer_id=alice.id,
            total_amount=50.0,
            items=["Test Case Cover"],
            status="delivered",
            order_id=unique_order_id,
        )
        order_id_str = str(new_order.id)

        # Process valid refund
        res = process_refund(order_id=order_id_str, customer_id=str(alice.id), reason="Wrong size")
        assert res.get("success") is True
        assert res["status"] == "refunded"
        assert res["refund_amount"] == 50.0
        assert res["refund_reason"] == "Wrong size"
    finally:
        session.close()
