import jwt
import pytest
from httpx import AsyncClient

from auth.tokens import ALGORITHM, SECRET_KEY


@pytest.fixture
async def registered_user(client: AsyncClient) -> dict:
    """Register a user and return the credentials."""
    response = await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    return {"email": "test@example.com", "password": "password123"}


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, registered_user: dict) -> None:
    response = await client.post(
        "/api/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_access_token_contains_user_id(
    client: AsyncClient, registered_user: dict
) -> None:
    response = await client.post(
        "/api/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    )
    data = response.json()
    payload = jwt.decode(data["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["type"] == "access"
    assert "sub" in payload
    assert "exp" in payload


@pytest.mark.asyncio
async def test_login_refresh_token_is_refresh_type(
    client: AsyncClient, registered_user: dict
) -> None:
    response = await client.post(
        "/api/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    )
    data = response.json()
    payload = jwt.decode(data["refresh_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["type"] == "refresh"


@pytest.mark.asyncio
async def test_login_access_token_expires_in_15_minutes(
    client: AsyncClient, registered_user: dict
) -> None:
    response = await client.post(
        "/api/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    )
    data = response.json()
    access_payload = jwt.decode(data["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    refresh_payload = jwt.decode(data["refresh_token"], SECRET_KEY, algorithms=[ALGORITHM])

    # Access token should expire much sooner than refresh token
    access_exp = access_payload["exp"]
    refresh_exp = refresh_payload["exp"]
    assert refresh_exp > access_exp


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, registered_user: dict) -> None:
    response = await client.post(
        "/api/auth/login",
        json={"email": registered_user["email"], "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_login_nonexistent_email(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "password123"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_login_same_error_for_bad_email_and_bad_password(
    client: AsyncClient, registered_user: dict
) -> None:
    """Login should not reveal whether the email exists (security best practice)."""
    bad_email = await client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "password123"},
    )
    bad_password = await client.post(
        "/api/auth/login",
        json={"email": registered_user["email"], "password": "wrongpassword"},
    )
    assert bad_email.status_code == bad_password.status_code == 401
    assert bad_email.json()["detail"] == bad_password.json()["detail"]
