"""Наполнение базы демонстрационными данными.

Запуск: ``python -m app.seed`` (или внутри контейнера).
Идемпотентно: повторный запуск не создаёт дубликаты.
"""
from decimal import Decimal

from sqlalchemy import select

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.cart import Cart
from app.models.category import Category
from app.models.product import Product
from app.models.review import Review
from app.models.user import User, UserRole

CATEGORIES = [
    ("Электроника", "Гаджеты, ноутбуки, смартфоны и аксессуары"),
    ("Книги", "Художественная и техническая литература"),
    ("Одежда", "Мужская и женская одежда"),
    ("Дом и сад", "Товары для дома, кухни и сада"),
]

PRODUCTS = [
    # (name, description, price, stock, image, category_name)
    ("Ноутбук Pro 14", "Лёгкий ноутбук для разработчиков, 16 ГБ RAM, 512 ГБ SSD",
     "129990.00", 15, "https://picsum.photos/seed/laptop/600", "Электроника"),
    ("Смартфон X12", "Флагманский смартфон с AMOLED-экраном 6.5\"",
     "89990.00", 30, "https://picsum.photos/seed/phone/600", "Электроника"),
    ("Беспроводные наушники Air", "Активное шумоподавление, 30 часов работы",
     "14990.00", 50, "https://picsum.photos/seed/buds/600", "Электроника"),
    ("Чистый код", "Роберт Мартин — о написании поддерживаемого кода",
     "1890.00", 100, "https://picsum.photos/seed/cleancode/600", "Книги"),
    ("Грокаем алгоритмы", "Иллюстрированное пособие по алгоритмам",
     "1490.00", 80, "https://picsum.photos/seed/algo/600", "Книги"),
    ("Футболка Basic", "Хлопковая футболка унисекс, разные цвета",
     "1290.00", 200, "https://picsum.photos/seed/tshirt/600", "Одежда"),
    ("Куртка Outdoor", "Водонепроницаемая куртка для походов",
     "8990.00", 25, "https://picsum.photos/seed/jacket/600", "Одежда"),
    ("Кофемашина Aroma", "Автоматическая кофемашина для дома",
     "34990.00", 10, "https://picsum.photos/seed/coffee/600", "Дом и сад"),
    ("Набор кастрюль Chef", "Набор из 5 кастрюль с антипригарным покрытием",
     "6990.00", 40, "https://picsum.photos/seed/pots/600", "Дом и сад"),
    ("Настольная лампа Lumen", "LED-лампа с регулировкой яркости",
     "2490.00", 60, "https://picsum.photos/seed/lamp/600", "Дом и сад"),
]


def seed() -> None:
    db = SessionLocal()
    try:
        # Администратор
        admin = db.scalar(select(User).where(User.email == settings.FIRST_ADMIN_EMAIL))
        if not admin:
            admin = User(
                email=settings.FIRST_ADMIN_EMAIL,
                full_name="Администратор",
                hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD),
                role=UserRole.admin,
            )
            admin.cart = Cart()
            db.add(admin)

        # Демо-покупатель
        customer = db.scalar(select(User).where(User.email == "customer@example.com"))
        if not customer:
            customer = User(
                email="customer@example.com",
                full_name="Иван Покупатель",
                hashed_password=hash_password("customer12345"),
                role=UserRole.customer,
            )
            customer.cart = Cart()
            db.add(customer)

        # Категории
        cat_by_name: dict[str, Category] = {}
        for name, desc in CATEGORIES:
            cat = db.scalar(select(Category).where(Category.name == name))
            if not cat:
                cat = Category(name=name, description=desc)
                db.add(cat)
            cat_by_name[name] = cat
        db.flush()

        # Товары
        for name, desc, price, stock, image, cat_name in PRODUCTS:
            exists = db.scalar(select(Product).where(Product.name == name))
            if not exists:
                db.add(
                    Product(
                        name=name,
                        description=desc,
                        price=Decimal(price),
                        stock=stock,
                        image_url=image,
                        category_id=cat_by_name[cat_name].id,
                    )
                )
        db.flush()

        # Пара отзывов для демонстрации
        first_product = db.scalar(select(Product).order_by(Product.id))
        if first_product:
            existing_review = db.scalar(
                select(Review).where(
                    Review.user_id == customer.id,
                    Review.product_id == first_product.id,
                )
            )
            if not existing_review:
                db.add(
                    Review(
                        user_id=customer.id,
                        product_id=first_product.id,
                        rating=5,
                        text="Отличный товар, рекомендую!",
                    )
                )

        db.commit()
        print("[OK] Seed-данные успешно загружены.")
        print(f"   Admin:    {settings.FIRST_ADMIN_EMAIL} / {settings.FIRST_ADMIN_PASSWORD}")
        print("   Customer: customer@example.com / customer12345")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
