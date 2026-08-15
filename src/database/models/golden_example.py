import uuid
from typing import Optional
from uuid import UUID as PyUUID
from sqlalchemy import String, Text, UUID, text
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from src.database.connection import Base


class GoldenExample(Base):
    __tablename__ = "golden_examples"

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    user_query: Mapped[str] = mapped_column(Text, nullable=False)
    perfect_response: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=True)

    def __repr__(self) -> str:
        return f"<GoldenExample(id={self.id!r}, category={self.category!r})>"
