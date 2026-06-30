"""Тесты регистрации и авторизации."""
from app.core.config import settings

API = settings.API_V1_PREFIX


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_register_and_login(client):
    resp = client.post(
        f"{API}/auth/register",
        json={"email": "u1@test.com", "full_name": "U1", "password": "password123"},
    )
    assert resp.status_code == 201
    assert resp.json()["email"] == "u1@test.com"
    assert resp.json()["role"] == "customer"

    login = client.post(
        f"{API}/auth/login",
        data={"username": "u1@test.com", "password": "password123"},
    )
    assert login.status_code == 200
    assert "access_token" in login.json()


def test_register_duplicate_email(client):
    payload = {"email": "dup@test.com", "password": "password123"}
    assert client.post(f"{API}/auth/register", json=payload).status_code == 201
    assert client.post(f"{API}/auth/register", json=payload).status_code == 400


def test_login_wrong_password(client):
    client.post(
        f"{API}/auth/register",
        json={"email": "u2@test.com", "password": "password123"},
    )
    resp = client.post(
        f"{API}/auth/login",
        data={"username": "u2@test.com", "password": "wrongpass"},
    )
    assert resp.status_code == 401


def test_me_requires_auth(client):
    assert client.get(f"{API}/auth/me").status_code == 401


def test_me_returns_profile(client, customer_headers):
    resp = client.get(f"{API}/auth/me", headers=customer_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "customer@test.com"
