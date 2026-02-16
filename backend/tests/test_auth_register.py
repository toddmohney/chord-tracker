import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "securepass123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    payload = {"email": "dupe@example.com", "password": "securepass123"}
    response1 = await client.post("/api/auth/register", json=payload)
    assert response1.status_code == 201

    response2 = await client.post("/api/auth/register", json=payload)
    assert response2.status_code == 409
    assert "already registered" in response2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/register",
        json={"email": "not-an-email", "password": "securepass123"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "short"},
    )
    assert response.status_code == 422
    body = response.json()
    detail_str = str(body["detail"])
    assert "8 characters" in detail_str.lower()


@pytest.mark.asyncio
async def test_register_missing_fields(client: AsyncClient) -> None:
    response = await client.post("/api/auth/register", json={})
    assert response.status_code == 422

    response = await client.post("/api/auth/register", json={"email": "test@example.com"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_password_is_hashed(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/register",
        json={"email": "hash@example.com", "password": "securepass123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "hash@example.com"
    assert "password_hash" not in data
