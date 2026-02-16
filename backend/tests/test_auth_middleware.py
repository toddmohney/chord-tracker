import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from httpx import AsyncClient

from auth.tokens import ALGORITHM, SECRET_KEY, create_access_token, create_refresh_token


@pytest.fixture
async def registered_user(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/auth/register",
        json={"email": "middleware@test.com", "password": "password123"},
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def access_token(registered_user: dict) -> str:
    return create_access_token(uuid.UUID(registered_user["id"]))


@pytest.mark.asyncio
async def test_protected_endpoint_with_valid_token(
    client: AsyncClient, registered_user: dict, access_token: str
) -> None:
    """Valid access token should allow access to protected endpoints."""
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == registered_user["id"]
    assert data["email"] == "middleware@test.com"


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client: AsyncClient) -> None:
    """Missing Authorization header should return 401."""
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_expired_token(
    client: AsyncClient, registered_user: dict
) -> None:
    """Expired access token should return 401."""
    payload = {
        "sub": registered_user["id"],
        "exp": datetime.now(UTC) - timedelta(minutes=1),
        "type": "access",
    }
    expired_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired"


@pytest.mark.asyncio
async def test_protected_endpoint_with_invalid_token(client: AsyncClient) -> None:
    """Invalid token should return 401."""
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@pytest.mark.asyncio
async def test_protected_endpoint_with_refresh_token(
    client: AsyncClient, registered_user: dict
) -> None:
    """Refresh token should not be accepted for protected endpoints."""
    refresh_token = create_refresh_token(uuid.UUID(registered_user["id"]))
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token type"


@pytest.mark.asyncio
async def test_protected_endpoint_with_nonexistent_user(client: AsyncClient) -> None:
    """Token for a user that doesn't exist should return 401."""
    fake_user_id = uuid.uuid4()
    token = create_access_token(fake_user_id)
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_protected_endpoint_returns_user_without_password(
    client: AsyncClient, registered_user: dict, access_token: str
) -> None:
    """Protected endpoint should not expose password hash."""
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "password_hash" not in data
    assert "password" not in data
