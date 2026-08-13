import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID as PyUUID
from sqlalchemy import String, Float, DateTime, ForeignKey, JSON, UUID, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.connection import Base

if TYPE_CHECKING:
    from src.database.models.customer import Customer


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    customer_id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="processing")
    
    total_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    delivery_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    items: Mapped[list] = mapped_column(JSON, nullable=False)

    # Refund details (populated when status == "refunded")
    refund_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    refund_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    refunded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="orders")

    def __repr__(self) -> str:
        return f"<Order(id={self.id!r}, status={self.status!r}, total_amount={self.total_amount!r})>"
