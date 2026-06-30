"""Эндпоинты заказов: создание из корзины, история, управление статусом."""
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.core.deps import get_current_admin, get_current_user
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.order import OrderRead, OrderStatusUpdate

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Order:
    """Создать заказ из текущей корзины. Списывает остатки и очищает корзину."""
    cart = db.scalar(
        select(Cart)
        .where(Cart.user_id == user.id)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
    )
    if not cart or not cart.items:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Корзина пуста")

    # Проверка остатков перед оформлением.
    for item in cart.items:
        if item.product.stock < item.quantity:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Недостаточно товара '{item.product.name}' на складе",
            )

    order = Order(user_id=user.id, total_price=Decimal("0.00"))
    db.add(order)
    db.flush()

    total = Decimal("0.00")
    for item in cart.items:
        price = Decimal(str(item.product.price))
        total += price * item.quantity
        item.product.stock -= item.quantity
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                product_name=item.product.name,
                price=price,
                quantity=item.quantity,
            )
        )
        db.delete(item)

    order.total_price = total
    db.commit()
    db.refresh(order)
    return order


@router.get("", response_model=list[OrderRead])
def my_orders(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[Order]:
    """История заказов текущего пользователя."""
    return list(
        db.scalars(
            select(Order)
            .where(Order.user_id == user.id)
            .options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
        )
    )


@router.get("/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Order:
    order = db.scalar(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items))
    )
    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Заказ не найден")
    if order.user_id != user.id and user.role.value != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Нет доступа к этому заказу")
    return order


@router.patch(
    "/{order_id}/status",
    response_model=OrderRead,
    dependencies=[Depends(get_current_admin)],
)
def update_status(
    order_id: int, payload: OrderStatusUpdate, db: Session = Depends(get_db)
) -> Order:
    """Изменить статус заказа (только admin)."""
    order = db.scalar(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items))
    )
    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Заказ не найден")
    order.status = payload.status
    db.commit()
    db.refresh(order)
    return order
