"""Точка входа FastAPI-приложения ecommerce-api-fastapi."""
from fastapi import FastAPI

from app.core.config import settings
from app.routers import auth, cart, categories, orders, products, reviews

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description=(
        "REST API интернет-магазина: пользователи и роли, каталог товаров, "
        "корзина, заказы и отзывы. Документация — /docs (Swagger) и /redoc."
    ),
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Проверка работоспособности сервиса."""
    return {"status": "ok"}


for r in (auth, categories, products, cart, orders, reviews):
    app.include_router(r.router, prefix=settings.API_V1_PREFIX)
