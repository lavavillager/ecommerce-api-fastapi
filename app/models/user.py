"""Модель пользователя и роли."""
import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
    """Роли пользователей системы."""

    admin = "admin"
    customer = "customer"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.customer, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    cart: Mapped["Cart"] = relationship(  # noqa: F821
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    orders: Mapped[list["Order"]] = relationship(  # noqa: F821
        back_populates="user", cascade="all, delete-orphan"
    )
    reviews: Mapped[list["Review"]] = relationship(  # noqa: F821
        back_populates="user", cascade="all, delete-orphan"
    )
