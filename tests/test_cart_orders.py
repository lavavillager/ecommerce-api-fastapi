"""Тесты корзины, заказов и отзывов."""
from app.core.config import settings

API = settings.API_V1_PREFIX


def _make_product(client, admin_headers, name="Товар", price="100.00", stock=10):
    return client.post(
        f"{API}/products",
        json={"name": name, "price": price, "stock": stock},
        headers=admin_headers,
    ).json()


def test_cart_flow(client, admin_headers, customer_headers):
    product = _make_product(client, admin_headers, price="100.00", stock=10)
    pid = product["id"]

    # Добавить
    resp = client.post(
        f"{API}/cart/items",
        json={"product_id": pid, "quantity": 2},
        headers=customer_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["total_price"] == "200.00"

    # Изменить количество
    resp = client.patch(
        f"{API}/cart/items/{pid}", json={"quantity": 3}, headers=customer_headers
    )
    assert resp.json()["total_price"] == "300.00"

    # Удалить позицию
    resp = client.delete(f"{API}/cart/items/{pid}", headers=customer_headers)
    assert resp.json()["items"] == []

    # Очистить корзину
    client.post(
        f"{API}/cart/items",
        json={"product_id": pid, "quantity": 1},
        headers=customer_headers,
    )
    assert client.delete(f"{API}/cart", headers=customer_headers).status_code == 204
    assert client.get(f"{API}/cart", headers=customer_headers).json()["items"] == []


def test_add_more_than_stock_fails(client, admin_headers, customer_headers):
    product = _make_product(client, admin_headers, stock=1)
    resp = client.post(
        f"{API}/cart/items",
        json={"product_id": product["id"], "quantity": 5},
        headers=customer_headers,
    )
    assert resp.status_code == 400


def test_order_from_cart(client, admin_headers, customer_headers):
    product = _make_product(client, admin_headers, price="150.00", stock=10)
    pid = product["id"]
    client.post(
        f"{API}/cart/items",
        json={"product_id": pid, "quantity": 2},
        headers=customer_headers,
    )

    order = client.post(f"{API}/orders", headers=customer_headers)
    assert order.status_code == 201
    body = order.json()
    assert body["status"] == "pending"
    assert body["total_price"] == "300.00"
    assert len(body["items"]) == 1

    # Остаток списан
    assert client.get(f"{API}/products/{pid}").json()["stock"] == 8
    # Корзина очищена
    assert client.get(f"{API}/cart", headers=customer_headers).json()["items"] == []
    # История заказов
    assert len(client.get(f"{API}/orders", headers=customer_headers).json()) == 1


def test_order_empty_cart_fails(client, customer_headers):
    assert client.post(f"{API}/orders", headers=customer_headers).status_code == 400


def test_admin_updates_order_status(client, admin_headers, customer_headers):
    product = _make_product(client, admin_headers)
    client.post(
        f"{API}/cart/items",
        json={"product_id": product["id"], "quantity": 1},
        headers=customer_headers,
    )
    order_id = client.post(f"{API}/orders", headers=customer_headers).json()["id"]

    resp = client.patch(
        f"{API}/orders/{order_id}/status",
        json={"status": "shipped"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "shipped"

    # Покупатель не может менять статус
    assert (
        client.patch(
            f"{API}/orders/{order_id}/status",
            json={"status": "paid"},
            headers=customer_headers,
        ).status_code
        == 403
    )


def test_review_flow(client, admin_headers, customer_headers):
    product = _make_product(client, admin_headers)
    pid = product["id"]

    resp = client.post(
        f"{API}/products/{pid}/reviews",
        json={"rating": 5, "text": "Супер"},
        headers=customer_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["rating"] == 5

    # Повторный отзыв запрещён
    assert (
        client.post(
            f"{API}/products/{pid}/reviews",
            json={"rating": 4},
            headers=customer_headers,
        ).status_code
        == 400
    )

    reviews = client.get(f"{API}/products/{pid}/reviews").json()
    assert len(reviews) == 1
