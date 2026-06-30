"""Схемы корзины."""
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.product import ProductRead


class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = Field(default=1, gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product: ProductRead
    quantity: int


class CartRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    items: list[CartItemRead]
    total_price: Decimal = Decimal("0.00")
