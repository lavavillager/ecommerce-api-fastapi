"""Эндпоинты корзины текущего пользователя."""
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import CartItemAdd, CartItemUpdate, CartRead

router = APIRouter(prefix="/cart", tags=["cart"])


def _get_or_create_cart(db: Session, user: User) -> Cart:
    cart = db.scalar(
        select(Cart)
        .where(Cart.user_id == user.id)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
    )
    if not cart:
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def _serialize(cart: Cart) -> CartRead:
    total = sum(
        (Decimal(str(i.product.price)) * i.quantity for i in cart.items),
        Decimal("0.00"),
    )
    data = CartRead.model_validate(cart)
    data.total_price = total
    return data


@router.get("", response_model=CartRead)
def get_cart(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> CartRead:
    return _serialize(_get_or_create_cart(db, user))


@router.post("/items", response_model=CartRead, status_code=status.HTTP_201_CREATED)
def add_item(
    payload: CartItemAdd,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CartRead:
    """Добавить товар в корзину (или увеличить количество существующей позиции)."""
    cart = _get_or_create_cart(db, user)
    product = db.get(Product, payload.product_id)
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Товар не найден")
    if product.stock < payload.quantity:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Недостаточно товара на складе")

    item = next(
        (i for i in cart.items if i.product_id == payload.product_id), None
    )
    if item:
        item.quantity += payload.quantity
    else:
        db.add(CartItem(cart_id=cart.id, product_id=product.id, quantity=payload.quantity))
    db.commit()
    return _serialize(_get_or_create_cart(db, user))


@router.patch("/items/{product_id}", response_model=CartRead)
def update_item(
    product_id: int,
    payload: CartItemUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CartRead:
    """Изменить количество товара в корзине."""
    cart = _get_or_create_cart(db, user)
    item = next((i for i in cart.items if i.product_id == product_id), None)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Позиция не найдена в корзине")
    item.quantity = payload.quantity
    db.commit()
    return _serialize(_get_or_create_cart(db, user))


@router.delete("/items/{product_id}", response_model=CartRead)
def remove_item(
    product_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CartRead:
    """Удалить товар из корзины."""
    cart = _get_or_create_cart(db, user)
    item = next((i for i in cart.items if i.product_id == product_id), None)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Позиция не найдена в корзине")
    db.delete(item)
    db.commit()
    return _serialize(_get_or_create_cart(db, user))


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> None:
    """Очистить корзину."""
    cart = _get_or_create_cart(db, user)
    for item in list(cart.items):
        db.delete(item)
    db.commit()
