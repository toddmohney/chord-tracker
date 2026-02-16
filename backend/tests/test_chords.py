import uuid

import pytest
from httpx import AsyncClient

from auth.tokens import create_access_token


@pytest.fixture
async def registered_user(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/auth/register",
        json={"email": "chords@test.com", "password": "password123"},
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
        json={"email": "other-chords@test.com", "password": "password123"},
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


SAMPLE_MARKERS = [{"string": 1, "fret": 2}, {"string": 2, "fret": 3}]


# --- List Chords ---


@pytest.mark.asyncio
async def test_list_chords_empty(client: AsyncClient, auth_headers: dict, song: dict) -> None:
    """Returns empty list when song has no chords."""
    response = await client.get(f"/api/songs/{song['id']}/chords", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_chords_ordered_by_position(
    client: AsyncClient, auth_headers: dict, song: dict
) -> None:
    """Returns chords ordered by position."""
    await client.post(
        f"/api/songs/{song['id']}/chords",
        json={"name": "Chord A", "markers": SAMPLE_MARKERS},
        headers=auth_headers,
    )
    await client.post(
        f"/api/songs/{song['id']}/chords",
        json={"name": "Chord B", "markers": SAMPLE_MARKERS},
        headers=auth_headers,
    )

    response = await client.get(f"/api/songs/{song['id']}/chords", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Chord A"
    assert data[0]["position"] == 0
    assert data[1]["name"] == "Chord B"
    assert data[1]["position"] == 1


@pytest.mark.asyncio
async def test_list_chords_validates_song_ownership(
    client: AsyncClient,
    other_auth_headers: dict,
    song: dict,
) -> None:
    """Returns 403 when listing chords for another user's song."""
    response = await client.get(f"/api/songs/{song['id']}/chords", headers=other_auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_chords_song_not_found(client: AsyncClient, auth_headers: dict) -> None:
    """Returns 404 for non-existent song."""
    fake_id = uuid.uuid4()
    response = await client.get(f"/api/songs/{fake_id}/chords", headers=auth_headers)
    assert response.status_code == 404


# --- Create Chord ---


@pytest.mark.asyncio
async def test_create_chord(client: AsyncClient, auth_headers: dict, song: dict) -> None:
    """Creates a chord with all fields and returns 201."""
    response = await client.post(
        f"/api/songs/{song['id']}/chords",
        json={
            "name": "Am",
            "markers": SAMPLE_MARKERS,
            "string_count": 6,
            "tuning": "EADGBE",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Am"
    assert data["markers"] == SAMPLE_MARKERS
    assert data["position"] == 0
    assert data["string_count"] == 6
    assert data["tuning"] == "EADGBE"
    assert data["song_id"] == song["id"]
    assert "id" in data


@pytest.mark.asyncio
async def test_create_chord_auto_position(
    client: AsyncClient, auth_headers: dict, song: dict
) -> None:
    """New chords auto-assign next position in sequence."""
    await client.post(
        f"/api/songs/{song['id']}/chords",
        json={"markers": SAMPLE_MARKERS},
        headers=auth_headers,
    )
    response = await client.post(
        f"/api/songs/{song['id']}/chords",
        json={"markers": SAMPLE_MARKERS},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["position"] == 1


@pytest.mark.asyncio
async def test_create_chord_defaults(client: AsyncClient, auth_headers: dict, song: dict) -> None:
    """Creates a chord with default values."""
    response = await client.post(
        f"/api/songs/{song['id']}/chords",
        json={"markers": []},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] is None
    assert data["markers"] == []
    assert data["string_count"] == 6
    assert data["tuning"] == "EADGBE"


@pytest.mark.asyncio
async def test_create_chord_in_other_users_song(
    client: AsyncClient, other_auth_headers: dict, song: dict
) -> None:
    """Returns 403 when creating a chord in another user's song."""
    response = await client.post(
        f"/api/songs/{song['id']}/chords",
        json={"markers": SAMPLE_MARKERS},
        headers=other_auth_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_chord_unauthenticated(client: AsyncClient, song: dict) -> None:
    """Returns 401 without auth."""
    response = await client.post(
        f"/api/songs/{song['id']}/chords",
        json={"markers": SAMPLE_MARKERS},
    )
    assert response.status_code == 401


# --- Update Chord ---


@pytest.mark.asyncio
async def test_update_chord(client: AsyncClient, auth_headers: dict, song: dict) -> None:
    """Updates chord fields."""
    create_resp = await client.post(
        f"/api/songs/{song['id']}/chords",
        json={"name": "Am", "markers": SAMPLE_MARKERS},
        headers=auth_headers,
    )
    chord_id = create_resp.json()["id"]

    new_markers = [{"string": 3, "fret": 4}]
    response = await client.put(
        f"/api/chords/{chord_id}",
        json={
            "name": "C",
            "markers": new_markers,
            "string_count": 7,
            "tuning": "BEADGBE",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "C"
    assert data["markers"] == new_markers
    assert data["string_count"] == 7
    assert data["tuning"] == "BEADGBE"


@pytest.mark.asyncio
async def test_update_chord_partial(client: AsyncClient, auth_headers: dict, song: dict) -> None:
    """Partial update only changes specified fields."""
    create_resp = await client.post(
        f"/api/songs/{song['id']}/chords",
        json={"name": "Am", "markers": SAMPLE_MARKERS},
        headers=auth_headers,
    )
    chord_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/chords/{chord_id}",
        json={"name": "Bm"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Bm"
    assert data["markers"] == SAMPLE_MARKERS  # unchanged


@pytest.mark.asyncio
async def test_update_chord_not_found(client: AsyncClient, auth_headers: dict) -> None:
    """Returns 404 for non-existent chord."""
    fake_id = uuid.uuid4()
    response = await client.put(
        f"/api/chords/{fake_id}",
        json={"name": "X"},
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_chord_forbidden(
    client: AsyncClient,
    auth_headers: dict,
    other_auth_headers: dict,
    song: dict,
) -> None:
    """Returns 403 when updating another user's chord."""
    create_resp = await client.post(
        f"/api/songs/{song['id']}/chords",
        json={"markers": SAMPLE_MARKERS},
        headers=auth_headers,
    )
    chord_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/chords/{chord_id}",
        json={"name": "Stolen"},
        headers=other_auth_headers,
    )
    assert response.status_code == 403


# --- Delete Chord ---


@pytest.mark.asyncio
async def test_delete_chord(client: AsyncClient, auth_headers: dict, song: dict) -> None:
    """Deletes a chord and returns 204."""
    create_resp = await client.post(
        f"/api/songs/{song['id']}/chords",
        json={"markers": SAMPLE_MARKERS},
        headers=auth_headers,
    )
    chord_id = create_resp.json()["id"]

    response = await client.delete(f"/api/chords/{chord_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify it's gone
    get_resp = await client.get(f"/api/songs/{song['id']}/chords", headers=auth_headers)
    assert len(get_resp.json()) == 0


@pytest.mark.asyncio
async def test_delete_chord_renormalizes_positions(
    client: AsyncClient, auth_headers: dict, song: dict
) -> None:
    """Deleting a chord re-normalizes positions of remaining chords."""
    # Create 3 chords at positions 0, 1, 2
    for name in ["A", "B", "C"]:
        await client.post(
            f"/api/songs/{song['id']}/chords",
            json={"name": name, "markers": SAMPLE_MARKERS},
            headers=auth_headers,
        )

    # Get all chords to find the middle one
    list_resp = await client.get(f"/api/songs/{song['id']}/chords", headers=auth_headers)
    chords = list_resp.json()
    middle_chord_id = chords[1]["id"]  # "B" at position 1

    # Delete middle chord
    await client.delete(f"/api/chords/{middle_chord_id}", headers=auth_headers)

    # Remaining chords should have positions 0, 1
    list_resp = await client.get(f"/api/songs/{song['id']}/chords", headers=auth_headers)
    remaining = list_resp.json()
    assert len(remaining) == 2
    assert remaining[0]["name"] == "A"
    assert remaining[0]["position"] == 0
    assert remaining[1]["name"] == "C"
    assert remaining[1]["position"] == 1


@pytest.mark.asyncio
async def test_delete_chord_not_found(client: AsyncClient, auth_headers: dict) -> None:
    """Returns 404 for non-existent chord."""
    fake_id = uuid.uuid4()
    response = await client.delete(f"/api/chords/{fake_id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_chord_forbidden(
    client: AsyncClient,
    auth_headers: dict,
    other_auth_headers: dict,
    song: dict,
) -> None:
    """Returns 403 when deleting another user's chord."""
    create_resp = await client.post(
        f"/api/songs/{song['id']}/chords",
        json={"markers": SAMPLE_MARKERS},
        headers=auth_headers,
    )
    chord_id = create_resp.json()["id"]

    response = await client.delete(f"/api/chords/{chord_id}", headers=other_auth_headers)
    assert response.status_code == 403

    # Verify it still exists
    list_resp = await client.get(f"/api/songs/{song['id']}/chords", headers=auth_headers)
    assert len(list_resp.json()) == 1


# --- Reorder Chords ---


@pytest.mark.asyncio
async def test_reorder_chords(client: AsyncClient, auth_headers: dict, song: dict) -> None:
    """Reorders chords and returns them in new order."""
    ids = []
    for name in ["A", "B", "C"]:
        resp = await client.post(
            f"/api/songs/{song['id']}/chords",
            json={"name": name, "markers": SAMPLE_MARKERS},
            headers=auth_headers,
        )
        ids.append(resp.json()["id"])

    # Reverse order: C, B, A
    response = await client.put(
        f"/api/songs/{song['id']}/chords/reorder",
        json={"chord_ids": list(reversed(ids))},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "C"
    assert data[0]["position"] == 0
    assert data[1]["name"] == "B"
    assert data[1]["position"] == 1
    assert data[2]["name"] == "A"
    assert data[2]["position"] == 2


@pytest.mark.asyncio
async def test_reorder_chords_invalid_ids(
    client: AsyncClient, auth_headers: dict, song: dict
) -> None:
    """Returns 400 when chord_ids don't match song's chords."""
    await client.post(
        f"/api/songs/{song['id']}/chords",
        json={"markers": SAMPLE_MARKERS},
        headers=auth_headers,
    )

    response = await client.put(
        f"/api/songs/{song['id']}/chords/reorder",
        json={"chord_ids": [str(uuid.uuid4())]},
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_reorder_chords_forbidden(
    client: AsyncClient,
    other_auth_headers: dict,
    song: dict,
) -> None:
    """Returns 403 when reordering another user's chords."""
    response = await client.put(
        f"/api/songs/{song['id']}/chords/reorder",
        json={"chord_ids": []},
        headers=other_auth_headers,
    )
    assert response.status_code == 403
