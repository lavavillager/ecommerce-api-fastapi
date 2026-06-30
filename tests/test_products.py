"""Тесты каталога товаров, фильтров и админских прав."""
from app.core.config import settings

API = settings.API_V1_PREFIX


def _create_category(client, headers, name="Электроника"):
    return client.post(
        f"{API}/categories", json={"name": name}, headers=headers
    ).json()


def _create_product(client, headers, **kwargs):
    payload = {
        "name": "Товар",
        "price": "100.00",
        "stock": 10,
        **kwargs,
    }
    return client.post(f"{API}/products", json=payload, headers=headers)


def test_customer_cannot_create_product(client, customer_headers):
    resp = _create_product(client, customer_headers)
    assert resp.status_code == 403


def test_admin_can_create_product(client, admin_headers):
    cat = _create_category(client, admin_headers)
    resp = _create_product(
        client, admin_headers, name="Ноутбук", price="1500.00", category_id=cat["id"]
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "Ноутбук"
    assert resp.json()["category"]["name"] == "Электроника"


def test_list_and_filter_products(client, admin_headers):
    cat = _create_category(client, admin_headers)
    _create_product(client, admin_headers, name="Дешёвый", price="50.00")
    _create_product(client, admin_headers, name="Дорогой", price="5000.00",
                    category_id=cat["id"])

    # Без фильтров
    resp = client.get(f"{API}/products")
    assert resp.json()["total"] == 2

    # Поиск по названию
    resp = client.get(f"{API}/products", params={"q": "Дорог"})
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["name"] == "Дорогой"

    # Фильтр по цене
    resp = client.get(f"{API}/products", params={"min_price": 1000})
    assert resp.json()["total"] == 1

    # Фильтр по категории
    resp = client.get(f"{API}/products", params={"category_id": cat["id"]})
    assert resp.json()["total"] == 1


def test_update_and_delete_product(client, admin_headers):
    pid = _create_product(client, admin_headers).json()["id"]

    upd = client.patch(
        f"{API}/products/{pid}", json={"price": "999.00"}, headers=admin_headers
    )
    assert upd.status_code == 200
    assert upd.json()["price"] == "999.00"

    delete = client.delete(f"{API}/products/{pid}", headers=admin_headers)
    assert delete.status_code == 204
    assert client.get(f"{API}/products/{pid}").status_code == 404
