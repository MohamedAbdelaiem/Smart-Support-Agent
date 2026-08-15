from src.agent import execute_tool
from src.tools.schemas import LOOKUP_ORDER_SCHEMA, PROCESS_REFUND_SCHEMA, LOOKUP_CUSTOMER_SCHEMA


def test_execute_tool_success():
    res = execute_tool("lookup_order", {"order_id": "ORD-1001"}, LOOKUP_ORDER_SCHEMA)
    assert res["status"] in ("delivered", "refunded")
    assert res["customer_name"] == "Alice Smith"


def test_execute_tool_lookup_customer():
    res = execute_tool("lookup_customer", {"name": "Alice Smith"}, LOOKUP_CUSTOMER_SCHEMA)
    assert "error" not in res
    assert res["name"] == "Alice Smith"
    assert "customer_id" in res


def test_execute_tool_process_refund_unauthorized():
    res = execute_tool(
        "process_refund",
        {"order_id": "ORD-1001", "customer_id": "c1000000-0000-0000-0000-000000000002"},
        PROCESS_REFUND_SCHEMA,
    )
    assert "error" in res
    assert "Unauthorized" in res["error"]


def test_execute_tool_missing_order():
    res = execute_tool("lookup_order", {"order_id": "ORD-9999"}, LOOKUP_ORDER_SCHEMA)
    assert "error" in res
    assert "No order found" in res["error"]


def test_execute_tool_invalid_args():
    res = execute_tool("lookup_order", {}, LOOKUP_ORDER_SCHEMA)
    assert "error" in res
    assert "Invalid arguments" in res["error"]


def test_execute_tool_unknown():
    res = execute_tool("unknown_tool", {})
    assert "error" in res
    assert "Unknown tool" in res["error"]
