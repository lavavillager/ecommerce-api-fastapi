# 🛒 ecommerce-api-fastapi

REST API бэкенда интернет-магазина на **FastAPI** с чистой архитектурой,
JWT-авторизацией, ролями, каталогом товаров, корзиной, заказами и отзывами.

Проект демонстрирует production-подход: разделение слоёв, миграции Alembic,
контейнеризация Docker, автотесты pytest и CI на GitHub Actions.

[![CI](https://github.com/USERNAME/ecommerce-api-fastapi/actions/workflows/ci.yml/badge.svg)](https://github.com/USERNAME/ecommerce-api-fastapi/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![Postgres](https://img.shields.io/badge/PostgreSQL-16-336791)

---

## ✨ Возможности

- 🔐 **Авторизация** — регистрация, вход, JWT access-токены.
- 👥 **Роли** — `admin` и `customer` с разграничением доступа.
- 🗂️ **Категории товаров** — CRUD (управление только для admin).
- 📦 **Товары** — название, описание, цена, остаток, категория, изображение.
- 🔎 **Фильтры каталога** — цена от/до, категория, поиск по названию, пагинация.
- 🛒 **Корзина** — добавить / изменить количество / удалить / очистить.
- 🧾 **Заказы** — оформление из корзины, списание остатков, статусы, история.
- ⭐ **Отзывы** — оценка (1–5) и текст, по одному отзыву на товар от пользователя.
- 🛠️ **Админ-эндпоинты** — управление товарами, категориями и статусами заказов.
- 🌱 **Seed-данные** — демонстрационные категории, товары и пользователи.
- 📑 **Swagger / OpenAPI** — интерактивная документация из коробки.

---

## 🧱 Технологический стек

| Категория        | Технологии                                   |
|------------------|----------------------------------------------|
| Язык             | Python 3.12                                  |
| Веб-фреймворк    | FastAPI, Uvicorn                             |
| Валидация        | Pydantic v2, pydantic-settings               |
| ORM / БД         | SQLAlchemy 2.0, PostgreSQL 16                |
| Миграции         | Alembic                                      |
| Авторизация      | JWT (python-jose), bcrypt                    |
| Тесты            | pytest, pytest-cov, httpx                    |
| Инфраструктура   | Docker, docker-compose, GitHub Actions       |

---

## 🏗️ Архитектура проекта

Проект построен по принципу разделения ответственности (clean layered architecture):

```
ecommerce-api-fastapi/
├── app/
│   ├── core/            # Конфигурация, БД, безопасность, зависимости
│   │   ├── config.py        # Настройки через переменные окружения
│   │   ├── database.py      # Engine, сессии, Base
│   │   ├── security.py      # Хеширование паролей и JWT
│   │   └── deps.py          # Зависимости: текущий пользователь, проверка ролей
│   ├── models/          # ORM-модели SQLAlchemy
│   ├── schemas/         # Pydantic-схемы (валидация ввода/вывода)
│   ├── routers/         # HTTP-эндпоинты по доменам
│   ├── seed.py          # Демонстрационные данные
│   └── main.py          # Точка входа FastAPI
├── alembic/             # Миграции БД
├── tests/               # Автотесты pytest
├── scripts/
│   └── entrypoint.sh    # Миграции + seed + запуск (в контейнере)
├── .github/workflows/   # CI (GitHub Actions)
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── requirements.txt
```

**Поток данных:** `router` (HTTP) → `schema` (валидация) → `model` (ORM) → PostgreSQL.
Зависимости (`deps.py`) инкапсулируют аутентификацию и авторизацию по ролям.

---

## 🚀 Быстрый старт (Docker)

Требуется установленный **Docker** и **Docker Compose**.

```bash
# 1. Клонировать репозиторий
git clone https://github.com/USERNAME/ecommerce-api-fastapi.git
cd ecommerce-api-fastapi

# 2. Создать .env из примера
cp .env.example .env

# 3. Запустить
docker compose up --build
```

При старте контейнер автоматически:
1. дождётся готовности PostgreSQL;
2. применит миграции Alembic (`alembic upgrade head`);
3. загрузит seed-данные;
4. запустит API на `http://localhost:8000`.

Документация:
- **Swagger UI** → http://localhost:8000/docs
- **ReDoc** → http://localhost:8000/redoc
- **Health-check** → http://localhost:8000/health

**Демо-учётные записи** (создаются при seed):

| Роль     | Email                  | Пароль          |
|----------|------------------------|-----------------|
| admin    | admin@example.com      | admin12345      |
| customer | customer@example.com   | customer12345   |

---

## 💻 Локальный запуск (без Docker)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

cp .env.example .env
# В .env укажите DATABASE_URL на локальный PostgreSQL, например:
# DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/ecommerce

alembic upgrade head             # применить миграции
python -m app.seed               # загрузить демо-данные
uvicorn app.main:app --reload    # запустить сервер
```

---

## 🧪 Тесты

Тесты используют изолированную in-memory SQLite — PostgreSQL для прогона не нужен.

```bash
pytest                       # запустить все тесты
pytest --cov=app             # с отчётом о покрытии
```

```
tests/test_auth.py ......
tests/test_cart_orders.py ......
tests/test_products.py ....
16 passed
```

---

## 🗄️ Миграции (Alembic)

```bash
alembic upgrade head                                   # применить миграции
alembic revision --autogenerate -m "описание"          # создать новую миграцию
alembic downgrade -1                                   # откатить последнюю
```

---

## 📡 Примеры API-запросов

> Базовый префикс: `/api/v1`. Полный список и схемы — в Swagger (`/docs`).
> Подробные примеры также в [docs/api-examples.md](docs/api-examples.md).

### Регистрация

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","full_name":"Иван","password":"password123"}'
```

### Вход (получение токена)

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin12345"
# => {"access_token":"<JWT>","token_type":"bearer"}
```

### Каталог с фильтрами

```bash
curl "http://localhost:8000/api/v1/products?q=ноут&min_price=1000&max_price=200000&category_id=1"
```

### Добавить товар в корзину

```bash
curl -X POST http://localhost:8000/api/v1/cart/items \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":2}'
```

### Оформить заказ из корзины

```bash
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Authorization: Bearer <JWT>"
```

### Создать товар (admin)

```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer <ADMIN_JWT>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Новый товар","price":"1990.00","stock":50,"category_id":1}'
```

---

## 🔌 Основные эндпоинты

| Метод  | Путь                                 | Доступ    | Назначение                       |
|--------|--------------------------------------|-----------|----------------------------------|
| POST   | `/api/v1/auth/register`              | публичный | Регистрация                      |
| POST   | `/api/v1/auth/login`                 | публичный | Получение JWT                    |
| GET    | `/api/v1/auth/me`                    | auth      | Профиль                          |
| GET    | `/api/v1/categories`                 | публичный | Список категорий                 |
| POST   | `/api/v1/categories`                 | admin     | Создать категорию                |
| GET    | `/api/v1/products`                   | публичный | Каталог с фильтрами              |
| POST   | `/api/v1/products`                   | admin     | Создать товар                    |
| PATCH  | `/api/v1/products/{id}`              | admin     | Обновить товар                   |
| DELETE | `/api/v1/products/{id}`              | admin     | Удалить товар                    |
| GET    | `/api/v1/cart`                       | auth      | Корзина                          |
| POST   | `/api/v1/cart/items`                 | auth      | Добавить в корзину               |
| PATCH  | `/api/v1/cart/items/{product_id}`    | auth      | Изменить количество              |
| DELETE | `/api/v1/cart/items/{product_id}`    | auth      | Удалить позицию                  |
| DELETE | `/api/v1/cart`                       | auth      | Очистить корзину                 |
| POST   | `/api/v1/orders`                     | auth      | Оформить заказ                   |
| GET    | `/api/v1/orders`                     | auth      | История заказов                  |
| PATCH  | `/api/v1/orders/{id}/status`         | admin     | Сменить статус заказа            |
| GET    | `/api/v1/products/{id}/reviews`      | публичный | Отзывы на товар                  |
| POST   | `/api/v1/products/{id}/reviews`      | auth      | Оставить отзыв                   |

Статусы заказа: `pending → paid → shipped → delivered` (или `cancelled`).

---

## ⚙️ Переменные окружения

См. [.env.example](.env.example). Ключевые:

| Переменная                    | Описание                          | По умолчанию           |
|-------------------------------|-----------------------------------|------------------------|
| `DATABASE_URL`                | Строка подключения к PostgreSQL   | `postgresql+psycopg2://postgres:postgres@db:5432/ecommerce` |
| `SECRET_KEY`                  | Секрет для подписи JWT            | `change-me-in-production` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни токена                | `1440`                 |
| `FIRST_ADMIN_EMAIL`           | Email администратора при seed     | `admin@example.com`    |
| `FIRST_ADMIN_PASSWORD`        | Пароль администратора при seed    | `admin12345`           |

> ⚠️ В production обязательно задайте свой `SECRET_KEY` (`openssl rand -hex 32`)
> и смените пароль администратора.

---

## 🤝 Публикация на GitHub

```bash
git init
git add .
git commit -m "feat: initial ecommerce API on FastAPI"
git branch -M main
git remote add origin https://github.com/USERNAME/ecommerce-api-fastapi.git
git push -u origin main
```

После push GitHub Actions автоматически прогонит миграции и тесты
(`.github/workflows/ci.yml`).

---

## 📄 Лицензия

MIT — свободно используйте в портфолио и коммерческих проектах.
