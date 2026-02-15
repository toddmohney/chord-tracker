import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from httpx import AsyncClient

from auth.tokens import ALGORITHM, SECRET_KEY


@pytest.fixture
async def login_tokens(client: AsyncClient) -> dict:
    """Register a user and log in, returning the token response."""
    await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    return response.json()


@pytest.mark.asyncio
async def test_refresh_returns_new_access_token(client: AsyncClient, login_tokens: dict) -> None:
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": login_tokens["refresh_token"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_refresh_access_token_is_valid(client: AsyncClient, login_tokens: dict) -> None:
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": login_tokens["refresh_token"]},
    )
    data = response.json()
    payload = jwt.decode(data["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["type"] == "access"
    assert "sub" in payload
    assert "exp" in payload


@pytest.mark.asyncio
async def test_refresh_with_expired_token(client: AsyncClient) -> None:
    expired_token = jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "exp": datetime.now(UTC) - timedelta(seconds=1),
            "type": "refresh",
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": expired_token},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token has expired"


@pytest.mark.asyncio
async def test_refresh_with_invalid_token(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": "not-a-valid-token"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"


@pytest.mark.asyncio
async def test_refresh_rejects_access_token(client: AsyncClient, login_tokens: dict) -> None:
    """Using an access token for refresh should be rejected."""
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": login_tokens["access_token"]},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"


@pytest.mark.asyncio
async def test_refresh_preserves_user_id(client: AsyncClient, login_tokens: dict) -> None:
    """The new access token should be for the same user."""
    original_payload = jwt.decode(login_tokens["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": login_tokens["refresh_token"]},
    )
    new_payload = jwt.decode(response.json()["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert new_payload["sub"] == original_payload["sub"]
