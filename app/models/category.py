"""Модель категории товаров."""
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    products: Mapped[list["Product"]] = relationship(  # noqa: F821
        back_populates="category"
    )
