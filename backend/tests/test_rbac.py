"""Tests for US-005: role-based permissions enforcement."""

import uuid

import pytest
from httpx import AsyncClient

from auth.tokens import create_access_token

# --- Shared fixtures ---


@pytest.fixture
async def owner(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/auth/register",
        json={"email": "rbac_owner@test.com", "password": "password123"},
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def owner_headers(owner: dict) -> dict[str, str]:
    token = create_access_token(uuid.UUID(owner["id"]))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def viewer_user(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/auth/register",
        json={"email": "rbac_viewer@test.com", "password": "password123"},
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def viewer_headers(viewer_user: dict) -> dict[str, str]:
    token = create_access_token(uuid.UUID(viewer_user["id"]))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def editor_user(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/auth/register",
        json={"email": "rbac_editor@test.com", "password": "password123"},
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def editor_headers(editor_user: dict) -> dict[str, str]:
    token = create_access_token(uuid.UUID(editor_user["id"]))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def project(client: AsyncClient, owner_headers: dict) -> dict:
    response = await client.post(
        "/api/projects", json={"name": "RBAC Test Project"}, headers=owner_headers
    )
    assert response.status_code == 201
    return response.json()


async def _accept_invitation(
    client: AsyncClient, project_id: str, invitee_email: str, role: str,
    owner_headers: dict, invitee_headers: dict
) -> str:
    """Helper: invite user, accept, return collaborator_id."""
    invite_resp = await client.post(
        f"/api/projects/{project_id}/collaborators",
        json={"identifier": invitee_email, "role": role},
        headers=owner_headers,
    )
    assert invite_resp.status_code == 201
    collab_id = invite_resp.json()["id"]

    patch_resp = await client.patch(
        f"/api/collaborators/{collab_id}",
        json={"status": "accepted"},
        headers=invitee_headers,
    )
    assert patch_resp.status_code == 200
    return collab_id


# --- GET /projects: includes collaborations ---


@pytest.mark.asyncio
async def test_list_projects_includes_accepted_collaboration(
    client: AsyncClient,
    owner_headers: dict,
    project: dict,
    viewer_user: dict,
    viewer_headers: dict,
) -> None:
    """GET /projects returns accepted collaborated projects."""
    await _accept_invitation(
        client, project["id"], viewer_user["email"], "viewer", owner_headers, viewer_headers
    )

    response = await client.get("/api/projects", headers=viewer_headers)
    assert response.status_code == 200
    data = response.json()
    project_ids = [p["id"] for p in data]
    assert project["id"] in project_ids


@pytest.mark.asyncio
async def test_list_projects_excludes_pending_collaboration(
    client: AsyncClient,
    owner_headers: dict,
    project: dict,
    viewer_user: dict,
    viewer_headers: dict,
) -> None:
    """GET /projects does not include projects with only pending invitations."""
    await client.post(
        f"/api/projects/{project['id']}/collaborators",
        json={"identifier": viewer_user["email"], "role": "viewer"},
        headers=owner_headers,
    )

    response = await client.get("/api/projects", headers=viewer_headers)
    assert response.status_code == 200
    project_ids = [p["id"] for p in response.json()]
    assert project["id"] not in project_ids


@pytest.mark.asyncio
async def test_list_projects_owner_has_my_role(
    client: AsyncClient, owner_headers: dict, project: dict
) -> None:
    """Owned projects have my_role='owner' in list response."""
    response = await client.get("/api/projects", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    owned = next(p for p in data if p["id"] == project["id"])
    assert owned["my_role"] == "owner"


@pytest.mark.asyncio
async def test_list_projects_collaborator_has_my_role(
    client: AsyncClient,
    owner_headers: dict,
    project: dict,
    viewer_user: dict,
    viewer_headers: dict,
) -> None:
    """Collaborated projects have the correct my_role in list response."""
    await _accept_invitation(
        client, project["id"], viewer_user["email"], "viewer", owner_headers, viewer_headers
    )

    response = await client.get("/api/projects", headers=viewer_headers)
    assert response.status_code == 200
    collab_project = next(p for p in response.json() if p["id"] == project["id"])
    assert collab_project["my_role"] == "viewer"


# --- GET /projects/{id}: my_role field ---


@pytest.mark.asyncio
async def test_get_project_owner_my_role(
    client: AsyncClient, owner_headers: dict, project: dict
) -> None:
    """GET /projects/{id} returns my_role='owner' for the owner."""
    response = await client.get(f"/api/projects/{project['id']}", headers=owner_headers)
    assert response.status_code == 200
    assert response.json()["my_role"] == "owner"


@pytest.mark.asyncio
async def test_get_project_collaborator_my_role(
    client: AsyncClient,
    owner_headers: dict,
    project: dict,
    editor_user: dict,
    editor_headers: dict,
) -> None:
    """GET /projects/{id} returns correct my_role for collaborator."""
    await _accept_invitation(
        client, project["id"], editor_user["email"], "editor", owner_headers, editor_headers
    )

    response = await client.get(f"/api/projects/{project['id']}", headers=editor_headers)
    assert response.status_code == 200
    assert response.json()["my_role"] == "editor"


@pytest.mark.asyncio
async def test_get_project_accessible_by_collaborator(
    client: AsyncClient,
    owner_headers: dict,
    project: dict,
    viewer_user: dict,
    viewer_headers: dict,
) -> None:
    """Accepted collaborator can GET the project detail."""
    await _accept_invitation(
        client, project["id"], viewer_user["email"], "viewer", owner_headers, viewer_headers
    )

    response = await client.get(f"/api/projects/{project['id']}", headers=viewer_headers)
    assert response.status_code == 200


# --- PUT /projects/{id}: only owner can rename ---


@pytest.mark.asyncio
async def test_update_project_editor_forbidden(
    client: AsyncClient,
    owner_headers: dict,
    project: dict,
    editor_user: dict,
    editor_headers: dict,
) -> None:
    """Editor cannot rename a project."""
    await _accept_invitation(
        client, project["id"], editor_user["email"], "editor", owner_headers, editor_headers
    )

    response = await client.put(
        f"/api/projects/{project['id']}", json={"name": "Stolen"}, headers=editor_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_project_viewer_forbidden(
    client: AsyncClient,
    owner_headers: dict,
    project: dict,
    viewer_user: dict,
    viewer_headers: dict,
) -> None:
    """Viewer cannot rename a project."""
    await _accept_invitation(
        client, project["id"], viewer_user["email"], "viewer", owner_headers, viewer_headers
    )

    response = await client.put(
        f"/api/projects/{project['id']}", json={"name": "Stolen"}, headers=viewer_headers
    )
    assert response.status_code == 403


# --- Songs: viewer cannot mutate ---


@pytest.fixture
async def song(client: AsyncClient, owner_headers: dict, project: dict) -> dict:
    response = await client.post(
        f"/api/projects/{project['id']}/songs",
        json={"name": "Test Song"},
        headers=owner_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_viewer_can_list_songs(
    client: AsyncClient,
    owner_headers: dict,
    project: dict,
    song: dict,
    viewer_user: dict,
    viewer_headers: dict,
) -> None:
    """Viewer can read songs."""
    await _accept_invitation(
        client, project["id"], viewer_user["email"], "viewer", owner_headers, viewer_headers
    )

    response = await client.get(
        f"/api/projects/{project['id']}/songs", headers=viewer_headers
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_viewer_cannot_create_song(
    client: AsyncClient,
    owner_headers: dict,
    project: dict,
    viewer_user: dict,
    viewer_headers: dict,
) -> None:
    """Viewer cannot create a song."""
    await _accept_invitation(
        client, project["id"], viewer_user["email"], "viewer", owner_headers, viewer_headers
    )

    response = await client.post(
        f"/api/projects/{project['id']}/songs",
        json={"name": "New Song"},
        headers=viewer_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_viewer_cannot_update_song(
    client: AsyncClient,
    owner_headers: dict,
    project: dict,
    song: dict,
    viewer_user: dict,
    viewer_headers: dict,
) -> None:
    """Viewer cannot update a song."""
    await _accept_invitation(
        client, project["id"], viewer_user["email"], "viewer", owner_headers, viewer_headers
    )

    response = await client.put(
        f"/api/songs/{song['id']}", json={"name": "Renamed"}, headers=viewer_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_viewer_cannot_delete_song(
    client: AsyncClient,
    owner_headers: dict,
    project: dict,
    song: dict,
    viewer_user: dict,
    viewer_headers: dict,
) -> None:
    """Viewer cannot delete a song."""
    await _accept_invitation(
        client, project["id"], viewer_user["email"], "viewer", owner_headers, viewer_headers
    )

    response = await client.delete(f"/api/songs/{song['id']}", headers=viewer_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_editor_can_create_song(
    client: AsyncClient,
    owner_headers: dict,
    project: dict,
    editor_user: dict,
    editor_headers: dict,
) -> None:
    """Editor can create a song."""
    await _accept_invitation(
        client, project["id"], editor_user["email"], "editor", owner_headers, editor_headers
    )

    response = await client.post(
        f"/api/projects/{project['id']}/songs",
        json={"name": "Editor's Song"},
        headers=editor_headers,
    )
    assert response.status_code == 201


# --- Collaborator management: editor/viewer cannot invite/remove/change-role ---


@pytest.mark.asyncio
async def test_editor_cannot_invite_collaborator(
    client: AsyncClient,
    owner_headers: dict,
    project: dict,
    editor_user: dict,
    editor_headers: dict,
    viewer_user: dict,
) -> None:
    """Editor cannot invite a collaborator."""
    await _accept_invitation(
        client, project["id"], editor_user["email"], "editor", owner_headers, editor_headers
    )

    response = await client.post(
        f"/api/projects/{project['id']}/collaborators",
        json={"identifier": viewer_user["email"], "role": "viewer"},
        headers=editor_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_viewer_cannot_change_collaborator_role(
    client: AsyncClient,
    owner_headers: dict,
    project: dict,
    viewer_user: dict,
    viewer_headers: dict,
    editor_user: dict,
    editor_headers: dict,
) -> None:
    """Viewer cannot change a collaborator's role."""
    editor_collab_id = await _accept_invitation(
        client, project["id"], editor_user["email"], "editor", owner_headers, editor_headers
    )
    await _accept_invitation(
        client, project["id"], viewer_user["email"], "viewer", owner_headers, viewer_headers
    )

    response = await client.patch(
        f"/api/projects/{project['id']}/collaborators/{editor_collab_id}",
        json={"role": "admin"},
        headers=viewer_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_viewer_cannot_remove_collaborator(
    client: AsyncClient,
    owner_headers: dict,
    project: dict,
    viewer_user: dict,
    viewer_headers: dict,
    editor_user: dict,
    editor_headers: dict,
) -> None:
    """Viewer cannot remove a collaborator."""
    editor_collab_id = await _accept_invitation(
        client, project["id"], editor_user["email"], "editor", owner_headers, editor_headers
    )
    await _accept_invitation(
        client, project["id"], viewer_user["email"], "viewer", owner_headers, viewer_headers
    )

    response = await client.delete(
        f"/api/projects/{project['id']}/collaborators/{editor_collab_id}",
        headers=viewer_headers,
    )
    assert response.status_code == 403
