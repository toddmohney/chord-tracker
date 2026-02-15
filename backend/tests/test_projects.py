import uuid

import pytest
from httpx import AsyncClient

from auth.tokens import create_access_token


@pytest.fixture
async def registered_user(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/auth/register",
        json={"email": "projects@test.com", "password": "password123"},
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def auth_headers(registered_user: dict) -> dict[str, str]:
    token = create_access_token(uuid.UUID(registered_user["id"]))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def other_user(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/auth/register",
        json={"email": "other@test.com", "password": "password123"},
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def other_auth_headers(other_user: dict) -> dict[str, str]:
    token = create_access_token(uuid.UUID(other_user["id"]))
    return {"Authorization": f"Bearer {token}"}


# --- List Projects ---


@pytest.mark.asyncio
async def test_list_projects_empty(client: AsyncClient, auth_headers: dict) -> None:
    """Returns empty list when user has no projects."""
    response = await client.get("/api/projects", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_projects_returns_own_projects(client: AsyncClient, auth_headers: dict) -> None:
    """Returns only projects belonging to the authenticated user."""
    await client.post("/api/projects", json={"name": "Project A"}, headers=auth_headers)
    await client.post("/api/projects", json={"name": "Project B"}, headers=auth_headers)

    response = await client.get("/api/projects", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = {p["name"] for p in data}
    assert names == {"Project A", "Project B"}


@pytest.mark.asyncio
async def test_list_projects_excludes_other_users(
    client: AsyncClient, auth_headers: dict, other_auth_headers: dict
) -> None:
    """User should not see other users' projects."""
    await client.post("/api/projects", json={"name": "My Project"}, headers=auth_headers)
    await client.post("/api/projects", json={"name": "Other Project"}, headers=other_auth_headers)

    response = await client.get("/api/projects", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "My Project"


# --- Create Project ---


@pytest.mark.asyncio
async def test_create_project(
    client: AsyncClient, auth_headers: dict, registered_user: dict
) -> None:
    """Creates a project and returns 201 with project data."""
    response = await client.post(
        "/api/projects", json={"name": "New Project"}, headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Project"
    assert data["user_id"] == registered_user["id"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_project_unauthenticated(client: AsyncClient) -> None:
    """Creating a project without auth returns 401."""
    response = await client.post("/api/projects", json={"name": "Test"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_project_empty_name(client: AsyncClient, auth_headers: dict) -> None:
    """Creating a project with empty name returns 422."""
    response = await client.post("/api/projects", json={"name": "  "}, headers=auth_headers)
    assert response.status_code == 422


# --- Get Project ---


@pytest.mark.asyncio
async def test_get_project(client: AsyncClient, auth_headers: dict) -> None:
    """Returns a single project by ID."""
    create_resp = await client.post(
        "/api/projects", json={"name": "Test Project"}, headers=auth_headers
    )
    project_id = create_resp.json()["id"]

    response = await client.get(f"/api/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Project"


@pytest.mark.asyncio
async def test_get_project_not_found(client: AsyncClient, auth_headers: dict) -> None:
    """Returns 404 for non-existent project."""
    fake_id = uuid.uuid4()
    response = await client.get(f"/api/projects/{fake_id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_project_forbidden(
    client: AsyncClient, auth_headers: dict, other_auth_headers: dict
) -> None:
    """Returns 403 when accessing another user's project."""
    create_resp = await client.post("/api/projects", json={"name": "Private"}, headers=auth_headers)
    project_id = create_resp.json()["id"]

    response = await client.get(f"/api/projects/{project_id}", headers=other_auth_headers)
    assert response.status_code == 403


# --- Update Project ---


@pytest.mark.asyncio
async def test_update_project(client: AsyncClient, auth_headers: dict) -> None:
    """Updates project name."""
    create_resp = await client.post(
        "/api/projects", json={"name": "Old Name"}, headers=auth_headers
    )
    project_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/projects/{project_id}", json={"name": "New Name"}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_update_project_not_found(client: AsyncClient, auth_headers: dict) -> None:
    """Returns 404 for non-existent project."""
    fake_id = uuid.uuid4()
    response = await client.put(
        f"/api/projects/{fake_id}", json={"name": "X"}, headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_project_forbidden(
    client: AsyncClient, auth_headers: dict, other_auth_headers: dict
) -> None:
    """Returns 403 when updating another user's project."""
    create_resp = await client.post("/api/projects", json={"name": "Mine"}, headers=auth_headers)
    project_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/projects/{project_id}", json={"name": "Stolen"}, headers=other_auth_headers
    )
    assert response.status_code == 403


# --- Delete Project ---


@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient, auth_headers: dict) -> None:
    """Deletes a project and returns 204."""
    create_resp = await client.post(
        "/api/projects", json={"name": "To Delete"}, headers=auth_headers
    )
    project_id = create_resp.json()["id"]

    response = await client.delete(f"/api/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify it's gone
    get_resp = await client.get(f"/api/projects/{project_id}", headers=auth_headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_project_not_found(client: AsyncClient, auth_headers: dict) -> None:
    """Returns 404 for non-existent project."""
    fake_id = uuid.uuid4()
    response = await client.delete(f"/api/projects/{fake_id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_project_forbidden(
    client: AsyncClient, auth_headers: dict, other_auth_headers: dict
) -> None:
    """Returns 403 when deleting another user's project."""
    create_resp = await client.post("/api/projects", json={"name": "Mine"}, headers=auth_headers)
    project_id = create_resp.json()["id"]

    response = await client.delete(f"/api/projects/{project_id}", headers=other_auth_headers)
    assert response.status_code == 403

    # Verify it still exists
    get_resp = await client.get(f"/api/projects/{project_id}", headers=auth_headers)
    assert get_resp.status_code == 200
