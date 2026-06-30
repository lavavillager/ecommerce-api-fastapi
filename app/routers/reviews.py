"""Эндпоинты отзывов на товары."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.product import Product
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewRead

router = APIRouter(tags=["reviews"])


@router.get("/products/{product_id}/reviews", response_model=list[ReviewRead])
def list_reviews(product_id: int, db: Session = Depends(get_db)) -> list[Review]:
    """Список отзывов на товар."""
    if not db.get(Product, product_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Товар не найден")
    return list(
        db.scalars(
            select(Review)
            .where(Review.product_id == product_id)
            .order_by(Review.created_at.desc())
        )
    )


@router.post(
    "/products/{product_id}/reviews",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
)
def create_review(
    product_id: int,
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Review:
    """Оставить отзыв на товар (один отзыв на пользователя и товар)."""
    if not db.get(Product, product_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Товар не найден")
    existing = db.scalar(
        select(Review).where(
            Review.product_id == product_id, Review.user_id == user.id
        )
    )
    if existing:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Вы уже оставили отзыв на этот товар"
        )
    review = Review(
        product_id=product_id,
        user_id=user.id,
        rating=payload.rating,
        text=payload.text,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.delete(
    "/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    """Удалить свой отзыв (или любой — администратору)."""
    review = db.get(Review, review_id)
    if not review:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Отзыв не найден")
    if review.user_id != user.id and user.role.value != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Нет доступа")
    db.delete(review)
    db.commit()
