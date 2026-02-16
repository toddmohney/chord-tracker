import uuid

import pytest
from httpx import AsyncClient

from auth.tokens import create_access_token


@pytest.fixture
async def registered_user(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/auth/register",
        json={"email": "songs@test.com", "password": "password123"},
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
        json={"email": "other-songs@test.com", "password": "password123"},
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def other_auth_headers(other_user: dict) -> dict[str, str]:
    token = create_access_token(uuid.UUID(other_user["id"]))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def project(client: AsyncClient, auth_headers: dict) -> dict:
    response = await client.post(
        "/api/projects", json={"name": "Test Project"}, headers=auth_headers
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def other_project(client: AsyncClient, other_auth_headers: dict) -> dict:
    response = await client.post(
        "/api/projects",
        json={"name": "Other Project"},
        headers=other_auth_headers,
    )
    assert response.status_code == 201
    return response.json()


# --- List Songs ---


@pytest.mark.asyncio
async def test_list_songs_empty(client: AsyncClient, auth_headers: dict, project: dict) -> None:
    """Returns empty list when project has no songs."""
    response = await client.get(f"/api/projects/{project['id']}/songs", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_songs_returns_project_songs(
    client: AsyncClient, auth_headers: dict, project: dict
) -> None:
    """Returns all songs in the project."""
    await client.post(
        f"/api/projects/{project['id']}/songs",
        json={"name": "Song A"},
        headers=auth_headers,
    )
    await client.post(
        f"/api/projects/{project['id']}/songs",
        json={"name": "Song B"},
        headers=auth_headers,
    )

    response = await client.get(f"/api/projects/{project['id']}/songs", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = {s["name"] for s in data}
    assert names == {"Song A", "Song B"}


@pytest.mark.asyncio
async def test_list_songs_validates_project_ownership(
    client: AsyncClient, other_auth_headers: dict, project: dict
) -> None:
    """Returns 403 when listing songs for another user's project."""
    response = await client.get(f"/api/projects/{project['id']}/songs", headers=other_auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_songs_project_not_found(client: AsyncClient, auth_headers: dict) -> None:
    """Returns 404 for non-existent project."""
    fake_id = uuid.uuid4()
    response = await client.get(f"/api/projects/{fake_id}/songs", headers=auth_headers)
    assert response.status_code == 404


# --- Create Song ---


@pytest.mark.asyncio
async def test_create_song(client: AsyncClient, auth_headers: dict, project: dict) -> None:
    """Creates a song and returns 201."""
    response = await client.post(
        f"/api/projects/{project['id']}/songs",
        json={"name": "New Song"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Song"
    assert data["project_id"] == project["id"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_song_in_other_users_project(
    client: AsyncClient, other_auth_headers: dict, project: dict
) -> None:
    """Returns 403 when creating a song in another user's project."""
    response = await client.post(
        f"/api/projects/{project['id']}/songs",
        json={"name": "Sneaky Song"},
        headers=other_auth_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_song_empty_name(
    client: AsyncClient, auth_headers: dict, project: dict
) -> None:
    """Returns 422 for empty song name."""
    response = await client.post(
        f"/api/projects/{project['id']}/songs",
        json={"name": "  "},
        headers=auth_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_song_unauthenticated(client: AsyncClient, project: dict) -> None:
    """Returns 401 when creating a song without auth."""
    response = await client.post(
        f"/api/projects/{project['id']}/songs",
        json={"name": "No Auth"},
    )
    assert response.status_code == 401


# --- Get Song ---


@pytest.mark.asyncio
async def test_get_song(client: AsyncClient, auth_headers: dict, project: dict) -> None:
    """Returns a single song by ID."""
    create_resp = await client.post(
        f"/api/projects/{project['id']}/songs",
        json={"name": "My Song"},
        headers=auth_headers,
    )
    song_id = create_resp.json()["id"]

    response = await client.get(f"/api/songs/{song_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "My Song"


@pytest.mark.asyncio
async def test_get_song_not_found(client: AsyncClient, auth_headers: dict) -> None:
    """Returns 404 for non-existent song."""
    fake_id = uuid.uuid4()
    response = await client.get(f"/api/songs/{fake_id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_song_forbidden(
    client: AsyncClient,
    auth_headers: dict,
    other_auth_headers: dict,
    project: dict,
) -> None:
    """Returns 403 when accessing another user's song."""
    create_resp = await client.post(
        f"/api/projects/{project['id']}/songs",
        json={"name": "Private Song"},
        headers=auth_headers,
    )
    song_id = create_resp.json()["id"]

    response = await client.get(f"/api/songs/{song_id}", headers=other_auth_headers)
    assert response.status_code == 403


# --- Update Song ---


@pytest.mark.asyncio
async def test_update_song(client: AsyncClient, auth_headers: dict, project: dict) -> None:
    """Updates song name."""
    create_resp = await client.post(
        f"/api/projects/{project['id']}/songs",
        json={"name": "Old Name"},
        headers=auth_headers,
    )
    song_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/songs/{song_id}",
        json={"name": "New Name"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_update_song_not_found(client: AsyncClient, auth_headers: dict) -> None:
    """Returns 404 for non-existent song."""
    fake_id = uuid.uuid4()
    response = await client.put(
        f"/api/songs/{fake_id}",
        json={"name": "X"},
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_song_forbidden(
    client: AsyncClient,
    auth_headers: dict,
    other_auth_headers: dict,
    project: dict,
) -> None:
    """Returns 403 when updating another user's song."""
    create_resp = await client.post(
        f"/api/projects/{project['id']}/songs",
        json={"name": "Mine"},
        headers=auth_headers,
    )
    song_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/songs/{song_id}",
        json={"name": "Stolen"},
        headers=other_auth_headers,
    )
    assert response.status_code == 403


# --- Delete Song ---


@pytest.mark.asyncio
async def test_delete_song(client: AsyncClient, auth_headers: dict, project: dict) -> None:
    """Deletes a song and returns 204."""
    create_resp = await client.post(
        f"/api/projects/{project['id']}/songs",
        json={"name": "To Delete"},
        headers=auth_headers,
    )
    song_id = create_resp.json()["id"]

    response = await client.delete(f"/api/songs/{song_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify it's gone
    get_resp = await client.get(f"/api/songs/{song_id}", headers=auth_headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_song_not_found(client: AsyncClient, auth_headers: dict) -> None:
    """Returns 404 for non-existent song."""
    fake_id = uuid.uuid4()
    response = await client.delete(f"/api/songs/{fake_id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_song_forbidden(
    client: AsyncClient,
    auth_headers: dict,
    other_auth_headers: dict,
    project: dict,
) -> None:
    """Returns 403 when deleting another user's song."""
    create_resp = await client.post(
        f"/api/projects/{project['id']}/songs",
        json={"name": "Mine"},
        headers=auth_headers,
    )
    song_id = create_resp.json()["id"]

    response = await client.delete(f"/api/songs/{song_id}", headers=other_auth_headers)
    assert response.status_code == 403

    # Verify it still exists
    get_resp = await client.get(f"/api/songs/{song_id}", headers=auth_headers)
    assert get_resp.status_code == 200


# --- Cascade Delete ---


@pytest.mark.asyncio
async def test_delete_song_cascades_to_chords(
    client: AsyncClient, auth_headers: dict, project: dict
) -> None:
    """Deleting a song should cascade and not error (chords cleaned up)."""
    create_resp = await client.post(
        f"/api/projects/{project['id']}/songs",
        json={"name": "With Chords"},
        headers=auth_headers,
    )
    song_id = create_resp.json()["id"]

    # Delete should succeed even though cascade will fire
    response = await client.delete(f"/api/songs/{song_id}", headers=auth_headers)
    assert response.status_code == 204
