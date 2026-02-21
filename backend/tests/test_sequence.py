import uuid

import pytest
from httpx import AsyncClient

from auth.tokens import create_access_token


@pytest.fixture
async def registered_user(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/auth/register",
        json={"email": "sequence@test.com", "password": "password123"},
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
        json={"email": "other-sequence@test.com", "password": "password123"},
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
        "/api/projects",
        json={"name": "Test Project"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def song(client: AsyncClient, auth_headers: dict, project: dict) -> dict:
    response = await client.post(
        f"/api/projects/{project['id']}/songs",
        json={"name": "Test Song"},
        headers=auth_headers,
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


@pytest.fixture
async def other_song(client: AsyncClient, other_auth_headers: dict, other_project: dict) -> dict:
    response = await client.post(
        f"/api/projects/{other_project['id']}/songs",
        json={"name": "Other Song"},
        headers=other_auth_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def sequence(client: AsyncClient, auth_headers: dict, song: dict) -> dict:
    response = await client.post(
        f"/api/songs/{song['id']}/sequence",
        json={},
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


# --- GET sequence ---


@pytest.mark.asyncio
async def test_get_sequence_not_found(
    client: AsyncClient, auth_headers: dict, song: dict
) -> None:
    """Returns 404 when no sequence exists."""
    response = await client.get(f"/api/songs/{song['id']}/sequence", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_sequence(
    client: AsyncClient, auth_headers: dict, song: dict, sequence: dict
) -> None:
    """Returns full sequence with nested measures and beats."""
    response = await client.get(f"/api/songs/{song['id']}/sequence", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sequence["id"]
    assert data["song_id"] == song["id"]
    assert data["time_signature_numerator"] == 4
    assert data["time_signature_denominator"] == 4
    assert data["measures_per_line"] == 4
    assert data["measures"] == []


@pytest.mark.asyncio
async def test_get_sequence_forbidden(
    client: AsyncClient, other_auth_headers: dict, song: dict, sequence: dict
) -> None:
    """Returns 403 when accessing another user's song's sequence."""
    response = await client.get(
        f"/api/songs/{song['id']}/sequence", headers=other_auth_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_sequence_song_not_found(client: AsyncClient, auth_headers: dict) -> None:
    """Returns 404 for non-existent song."""
    fake_id = uuid.uuid4()
    response = await client.get(f"/api/songs/{fake_id}/sequence", headers=auth_headers)
    assert response.status_code == 404


# --- POST sequence ---


@pytest.mark.asyncio
async def test_create_sequence_defaults(
    client: AsyncClient, auth_headers: dict, song: dict
) -> None:
    """Creates a sequence with default time signature settings."""
    response = await client.post(
        f"/api/songs/{song['id']}/sequence",
        json={},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["song_id"] == song["id"]
    assert data["time_signature_numerator"] == 4
    assert data["time_signature_denominator"] == 4
    assert data["measures_per_line"] == 4
    assert data["measures"] == []
    assert "id" in data


@pytest.mark.asyncio
async def test_create_sequence_custom_time_sig(
    client: AsyncClient, auth_headers: dict, song: dict
) -> None:
    """Creates a sequence with custom time signature."""
    response = await client.post(
        f"/api/songs/{song['id']}/sequence",
        json={"time_signature_numerator": 3, "time_signature_denominator": 4},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["time_signature_numerator"] == 3
    assert data["time_signature_denominator"] == 4


@pytest.mark.asyncio
async def test_create_sequence_conflict(
    client: AsyncClient, auth_headers: dict, song: dict, sequence: dict
) -> None:
    """Returns 409 when a sequence already exists for the song."""
    response = await client.post(
        f"/api/songs/{song['id']}/sequence",
        json={},
        headers=auth_headers,
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_sequence_forbidden(
    client: AsyncClient, other_auth_headers: dict, song: dict
) -> None:
    """Returns 403 when creating a sequence for another user's song."""
    response = await client.post(
        f"/api/songs/{song['id']}/sequence",
        json={},
        headers=other_auth_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_sequence_unauthenticated(client: AsyncClient, song: dict) -> None:
    """Returns 401 without auth."""
    response = await client.post(f"/api/songs/{song['id']}/sequence", json={})
    assert response.status_code == 401


# --- PUT sequence ---


@pytest.mark.asyncio
async def test_update_sequence_with_measures_and_beats(
    client: AsyncClient, auth_headers: dict, song: dict, sequence: dict
) -> None:
    """Replaces sequence with new measures and beats."""
    payload = {
        "time_signature_numerator": 3,
        "time_signature_denominator": 4,
        "measures_per_line": 2,
        "measures": [
            {
                "position": 0,
                "repeat_start": True,
                "repeat_end": False,
                "ending_number": None,
                "beats": [
                    {"beat_position": 1, "chord_id": None},
                    {"beat_position": 2, "chord_id": None},
                    {"beat_position": 3, "chord_id": None},
                ],
            },
            {
                "position": 1,
                "repeat_start": False,
                "repeat_end": True,
                "ending_number": 1,
                "beats": [],
            },
        ],
    }
    response = await client.put(
        f"/api/songs/{song['id']}/sequence",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["time_signature_numerator"] == 3
    assert data["time_signature_denominator"] == 4
    assert data["measures_per_line"] == 2
    assert len(data["measures"]) == 2

    m0 = data["measures"][0]
    assert m0["position"] == 0
    assert m0["repeat_start"] is True
    assert m0["repeat_end"] is False
    assert m0["ending_number"] is None
    assert len(m0["beats"]) == 3
    assert m0["beats"][0]["beat_position"] == 1

    m1 = data["measures"][1]
    assert m1["position"] == 1
    assert m1["repeat_end"] is True
    assert m1["ending_number"] == 1
    assert m1["beats"] == []


@pytest.mark.asyncio
async def test_update_sequence_replaces_existing_measures(
    client: AsyncClient, auth_headers: dict, song: dict, sequence: dict
) -> None:
    """PUT replaces all existing measures, not appending."""
    # First PUT with 2 measures
    await client.put(
        f"/api/songs/{song['id']}/sequence",
        json={"measures": [{"position": 0, "beats": []}, {"position": 1, "beats": []}]},
        headers=auth_headers,
    )

    # Second PUT with 1 measure - should replace, not append
    response = await client.put(
        f"/api/songs/{song['id']}/sequence",
        json={"measures": [{"position": 0, "beats": []}]},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["measures"]) == 1


@pytest.mark.asyncio
async def test_update_sequence_not_found(
    client: AsyncClient, auth_headers: dict, song: dict
) -> None:
    """Returns 404 when no sequence exists."""
    response = await client.put(
        f"/api/songs/{song['id']}/sequence",
        json={"measures": []},
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_sequence_forbidden(
    client: AsyncClient, other_auth_headers: dict, song: dict, sequence: dict
) -> None:
    """Returns 403 when updating another user's song's sequence."""
    response = await client.put(
        f"/api/songs/{song['id']}/sequence",
        json={"measures": []},
        headers=other_auth_headers,
    )
    assert response.status_code == 403


# --- DELETE sequence ---


@pytest.mark.asyncio
async def test_delete_sequence(
    client: AsyncClient, auth_headers: dict, song: dict, sequence: dict
) -> None:
    """Deletes sequence and returns 204."""
    response = await client.delete(
        f"/api/songs/{song['id']}/sequence", headers=auth_headers
    )
    assert response.status_code == 204

    # Verify it's gone
    get_resp = await client.get(f"/api/songs/{song['id']}/sequence", headers=auth_headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_sequence_with_measures(
    client: AsyncClient, auth_headers: dict, song: dict, sequence: dict
) -> None:
    """Deletes sequence and all child records."""
    # Add measures and beats first
    await client.put(
        f"/api/songs/{song['id']}/sequence",
        json={
            "measures": [
                {"position": 0, "beats": [{"beat_position": 1, "chord_id": None}]},
            ]
        },
        headers=auth_headers,
    )

    response = await client.delete(
        f"/api/songs/{song['id']}/sequence", headers=auth_headers
    )
    assert response.status_code == 204

    get_resp = await client.get(f"/api/songs/{song['id']}/sequence", headers=auth_headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_sequence_not_found(
    client: AsyncClient, auth_headers: dict, song: dict
) -> None:
    """Returns 404 when no sequence exists."""
    response = await client.delete(
        f"/api/songs/{song['id']}/sequence", headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_sequence_forbidden(
    client: AsyncClient, auth_headers: dict, other_auth_headers: dict, song: dict, sequence: dict
) -> None:
    """Returns 403 when deleting another user's song's sequence."""
    response = await client.delete(
        f"/api/songs/{song['id']}/sequence", headers=other_auth_headers
    )
    assert response.status_code == 403

    # Verify it still exists
    get_resp = await client.get(f"/api/songs/{song['id']}/sequence", headers=auth_headers)
    assert get_resp.status_code == 200
