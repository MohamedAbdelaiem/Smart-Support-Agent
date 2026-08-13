import uuid
from uuid import UUID as PyUUID


def parse_uuid(val: str | PyUUID) -> PyUUID:
    """Parses a string or PyUUID into a UUID, using UUID v5 if given a custom string like 'ORD-1001'."""
    if isinstance(val, PyUUID):
        return val
    try:
        return PyUUID(val)
    except (ValueError, TypeError):
        return uuid.uuid5(uuid.NAMESPACE_DNS, val)
