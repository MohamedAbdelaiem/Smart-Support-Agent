import uuid
from typing import TYPE_CHECKING, List
from uuid import UUID as PyUUID
from sqlalchemy import String, UUID, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.connection import Base

if TYPE_CHECKING:
    from src.database.models.order import Order


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="customer")

    def __repr__(self) -> str:
        return f"<Customer(id={self.id!r}, name={self.name!r})>"
