from src.agent import execute_tool
from src.tools.schemas import LOOKUP_ORDER_SCHEMA

def test_execute_tool_success():
    res = execute_tool("lookup_order", {"order_id": "ORD-1001"}, LOOKUP_ORDER_SCHEMA)
    assert res["status"] == "delivered"
    assert res["customer_name"] == "Alice Smith"

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
