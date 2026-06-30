"""Модель товара."""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(default=0, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    category: Mapped["Category | None"] = relationship(  # noqa: F821
        back_populates="products"
    )
    reviews: Mapped[list["Review"]] = relationship(  # noqa: F821
        back_populates="product", cascade="all, delete-orphan"
    )
