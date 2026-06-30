# Примеры API-запросов

Базовый URL: `http://localhost:8000/api/v1`. Для защищённых эндпоинтов
подставьте JWT в заголовок `Authorization: Bearer <token>`.

## 1. Аутентификация

### Регистрация
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","full_name":"Иван Иванов","password":"password123"}'
```
Ответ `201`:
```json
{"id": 3, "email": "user@example.com", "full_name": "Иван Иванов",
 "role": "customer", "is_active": true, "created_at": "2026-06-30T10:00:00Z"}
```

### Вход
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=user@example.com&password=password123"
```
```json
{"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "token_type": "bearer"}
```

### Текущий профиль
```bash
curl http://localhost:8000/api/v1/auth/me -H "Authorization: Bearer $TOKEN"
```

## 2. Категории

```bash
# Список (публично)
curl http://localhost:8000/api/v1/categories

# Создать (admin)
curl -X POST http://localhost:8000/api/v1/categories \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Аксессуары","description":"Чехлы, кабели и прочее"}'
```

## 3. Товары и фильтры

```bash
# Каталог
curl "http://localhost:8000/api/v1/products"

# Поиск по названию + цена от/до + категория + пагинация
curl "http://localhost:8000/api/v1/products?q=ноут&min_price=1000&max_price=200000&category_id=1&skip=0&limit=20"

# Создать товар (admin)
curl -X POST http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "Механическая клавиатура",
        "description": "Switch Brown, RGB",
        "price": "5990.00",
        "stock": 100,
        "image_url": "https://picsum.photos/seed/kbd/600",
        "category_id": 1
      }'

# Обновить товар (admin)
curl -X PATCH http://localhost:8000/api/v1/products/1 \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"price":"4990.00","stock":120}'

# Удалить товар (admin)
curl -X DELETE http://localhost:8000/api/v1/products/1 \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

## 4. Корзина

```bash
# Добавить товар
curl -X POST http://localhost:8000/api/v1/cart/items \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":2,"quantity":3}'

# Изменить количество
curl -X PATCH http://localhost:8000/api/v1/cart/items/2 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity":5}'

# Удалить позицию
curl -X DELETE http://localhost:8000/api/v1/cart/items/2 \
  -H "Authorization: Bearer $TOKEN"

# Просмотреть корзину
curl http://localhost:8000/api/v1/cart -H "Authorization: Bearer $TOKEN"

# Очистить корзину
curl -X DELETE http://localhost:8000/api/v1/cart -H "Authorization: Bearer $TOKEN"
```

## 5. Заказы

```bash
# Оформить заказ из корзины
curl -X POST http://localhost:8000/api/v1/orders -H "Authorization: Bearer $TOKEN"

# История заказов
curl http://localhost:8000/api/v1/orders -H "Authorization: Bearer $TOKEN"

# Один заказ
curl http://localhost:8000/api/v1/orders/1 -H "Authorization: Bearer $TOKEN"

# Сменить статус (admin): pending|paid|shipped|delivered|cancelled
curl -X PATCH http://localhost:8000/api/v1/orders/1/status \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"shipped"}'
```

## 6. Отзывы

```bash
# Оставить отзыв
curl -X POST http://localhost:8000/api/v1/products/2/reviews \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"rating":5,"text":"Отличный товар!"}'

# Список отзывов товара (публично)
curl http://localhost:8000/api/v1/products/2/reviews
```
