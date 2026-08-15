from fastapi import APIRouter, HTTPException
from src.tools.customer_lookup import list_customers

router = APIRouter(prefix="/api/customers", tags=["Customers"])


@router.get("")
def get_all_customers():
    """Returns list of active customers in PostgreSQL for UI dropdown selection."""
    try:
        return {"customers": list_customers()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch customers: {str(e)}")
