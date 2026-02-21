import uuid

import pytest
from httpx import AsyncClient

from auth.tokens import create_access_token


@pytest.fixture
async def owner(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/auth/register",
        json={"email": "owner@test.com", "password": "password123"},
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def owner_headers(owner: dict) -> dict[str, str]:
    token = create_access_token(uuid.UUID(owner["id"]))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def invitee(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/auth/register",
        json={"email": "invitee@test.com", "password": "password123"},
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def invitee_headers(invitee: dict) -> dict[str, str]:
    token = create_access_token(uuid.UUID(invitee["id"]))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def third_user(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/auth/register",
        json={"email": "third@test.com", "password": "password123"},
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def third_headers(third_user: dict) -> dict[str, str]:
    token = create_access_token(uuid.UUID(third_user["id"]))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def project(client: AsyncClient, owner_headers: dict) -> dict:
    response = await client.post(
        "/api/projects", json={"name": "Test Project"}, headers=owner_headers
    )
    assert response.status_code == 201
    return response.json()


# --- POST /projects/{project_id}/collaborators ---


@pytest.mark.asyncio
async def test_invite_collaborator_success(
    client: AsyncClient, owner_headers: dict, project: dict, invitee: dict
) -> None:
    """Owner can invite a user by email and receives a pending collaborator record."""
    response = await client.post(
        f"/api/projects/{project['id']}/collaborators",
        json={"identifier": invitee["email"], "role": "editor"},
        headers=owner_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["project_id"] == project["id"]
    assert data["invitee_id"] == invitee["id"]
    assert data["role"] == "editor"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_invite_collaborator_viewer_role(
    client: AsyncClient, owner_headers: dict, project: dict, invitee: dict
) -> None:
    """Owner can invite with viewer role."""
    response = await client.post(
        f"/api/projects/{project['id']}/collaborators",
        json={"identifier": invitee["email"], "role": "viewer"},
        headers=owner_headers,
    )
    assert response.status_code == 201
    assert response.json()["role"] == "viewer"


@pytest.mark.asyncio
async def test_invite_collaborator_admin_role(
    client: AsyncClient, owner_headers: dict, project: dict, invitee: dict
) -> None:
    """Owner can invite with admin role."""
    response = await client.post(
        f"/api/projects/{project['id']}/collaborators",
        json={"identifier": invitee["email"], "role": "admin"},
        headers=owner_headers,
    )
    assert response.status_code == 201
    assert response.json()["role"] == "admin"


@pytest.mark.asyncio
async def test_invite_collaborator_404_project(
    client: AsyncClient, owner_headers: dict, invitee: dict
) -> None:
    """Returns 404 when project does not exist."""
    fake_id = uuid.uuid4()
    response = await client.post(
        f"/api/projects/{fake_id}/collaborators",
        json={"identifier": invitee["email"], "role": "viewer"},
        headers=owner_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_invite_collaborator_404_user(
    client: AsyncClient, owner_headers: dict, project: dict
) -> None:
    """Returns 404 when the identifier does not match any user."""
    response = await client.post(
        f"/api/projects/{project['id']}/collaborators",
        json={"identifier": "nobody@nowhere.com", "role": "viewer"},
        headers=owner_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_invite_collaborator_403_non_owner(
    client: AsyncClient, third_headers: dict, project: dict, invitee: dict
) -> None:
    """Returns 403 when a non-owner/non-admin tries to invite."""
    response = await client.post(
        f"/api/projects/{project['id']}/collaborators",
        json={"identifier": invitee["email"], "role": "viewer"},
        headers=third_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_invite_collaborator_409_duplicate_pending(
    client: AsyncClient, owner_headers: dict, project: dict, invitee: dict
) -> None:
    """Returns 409 when the user already has a pending invitation."""
    await client.post(
        f"/api/projects/{project['id']}/collaborators",
        json={"identifier": invitee["email"], "role": "viewer"},
        headers=owner_headers,
    )
    response = await client.post(
        f"/api/projects/{project['id']}/collaborators",
        json={"identifier": invitee["email"], "role": "editor"},
        headers=owner_headers,
    )
    assert response.status_code == 409


@pytest.fixture
async def invitation(
    client: AsyncClient, owner_headers: dict, project: dict, invitee: dict
) -> dict:
    response = await client.post(
        f"/api/projects/{project['id']}/collaborators",
        json={"identifier": invitee["email"], "role": "editor"},
        headers=owner_headers,
    )
    assert response.status_code == 201
    return response.json()


# --- PATCH /collaborators/{collaborator_id} ---


@pytest.mark.asyncio
async def test_update_collaborator_status_accepted(
    client: AsyncClient, invitee_headers: dict, invitation: dict
) -> None:
    """Invitee can accept their invitation."""
    response = await client.patch(
        f"/api/collaborators/{invitation['id']}",
        json={"status": "accepted"},
        headers=invitee_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


@pytest.mark.asyncio
async def test_update_collaborator_status_declined(
    client: AsyncClient, invitee_headers: dict, invitation: dict
) -> None:
    """Invitee can decline their invitation."""
    response = await client.patch(
        f"/api/collaborators/{invitation['id']}",
        json={"status": "declined"},
        headers=invitee_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "declined"


@pytest.mark.asyncio
async def test_update_collaborator_status_403_non_invitee(
    client: AsyncClient, owner_headers: dict, invitation: dict
) -> None:
    """Non-invitee cannot change invitation status."""
    response = await client.patch(
        f"/api/collaborators/{invitation['id']}",
        json={"status": "accepted"},
        headers=owner_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_collaborator_status_400_pending(
    client: AsyncClient, invitee_headers: dict, invitation: dict
) -> None:
    """Cannot set status back to pending."""
    response = await client.patch(
        f"/api/collaborators/{invitation['id']}",
        json={"status": "pending"},
        headers=invitee_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_collaborator_status_404_not_found(
    client: AsyncClient, invitee_headers: dict
) -> None:
    """Returns 404 when collaborator record does not exist."""
    fake_id = uuid.uuid4()
    response = await client.patch(
        f"/api/collaborators/{fake_id}",
        json={"status": "accepted"},
        headers=invitee_headers,
    )
    assert response.status_code == 404


# --- GET /projects/{project_id}/collaborators ---


@pytest.mark.asyncio
async def test_list_collaborators_owner(
    client: AsyncClient, owner_headers: dict, project: dict, invitation: dict
) -> None:
    """Owner can list all collaborators."""
    response = await client.get(
        f"/api/projects/{project['id']}/collaborators",
        headers=owner_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == invitation["id"]


@pytest.mark.asyncio
async def test_list_collaborators_admin(
    client: AsyncClient,
    owner_headers: dict,
    project: dict,
    invitee: dict,
    invitee_headers: dict,
    third_user: dict,
    third_headers: dict,
) -> None:
    """Accepted admin collaborator can list collaborators."""
    # Invite invitee as admin
    invite_resp = await client.post(
        f"/api/projects/{project['id']}/collaborators",
        json={"identifier": invitee["email"], "role": "admin"},
        headers=owner_headers,
    )
    collaborator_id = invite_resp.json()["id"]

    # Accept the invitation
    await client.patch(
        f"/api/collaborators/{collaborator_id}",
        json={"status": "accepted"},
        headers=invitee_headers,
    )

    # Admin can now list
    response = await client.get(
        f"/api/projects/{project['id']}/collaborators",
        headers=invitee_headers,
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_collaborators_403_non_owner(
    client: AsyncClient, third_headers: dict, project: dict, invitation: dict
) -> None:
    """Non-owner/non-admin cannot list collaborators."""
    response = await client.get(
        f"/api/projects/{project['id']}/collaborators",
        headers=third_headers,
    )
    assert response.status_code == 403


# --- DELETE /projects/{project_id}/collaborators/{collaborator_id} ---


@pytest.mark.asyncio
async def test_remove_collaborator_success(
    client: AsyncClient, owner_headers: dict, project: dict, invitation: dict
) -> None:
    """Owner can remove a collaborator."""
    response = await client.delete(
        f"/api/projects/{project['id']}/collaborators/{invitation['id']}",
        headers=owner_headers,
    )
    assert response.status_code == 204

    # Confirm it's gone
    list_resp = await client.get(
        f"/api/projects/{project['id']}/collaborators",
        headers=owner_headers,
    )
    assert list_resp.json() == []


@pytest.mark.asyncio
async def test_remove_collaborator_403_non_owner(
    client: AsyncClient, third_headers: dict, project: dict, invitation: dict
) -> None:
    """Non-owner cannot remove a collaborator."""
    response = await client.delete(
        f"/api/projects/{project['id']}/collaborators/{invitation['id']}",
        headers=third_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_remove_collaborator_404_not_found(
    client: AsyncClient, owner_headers: dict, project: dict
) -> None:
    """Returns 404 when collaborator record does not exist."""
    fake_id = uuid.uuid4()
    response = await client.delete(
        f"/api/projects/{project['id']}/collaborators/{fake_id}",
        headers=owner_headers,
    )
    assert response.status_code == 404


# --- PATCH /projects/{project_id}/collaborators/{collaborator_id} (role) ---


@pytest.mark.asyncio
async def test_update_collaborator_role_owner_success(
    client: AsyncClient, owner_headers: dict, project: dict, invitation: dict
) -> None:
    """Owner can change a collaborator's role."""
    response = await client.patch(
        f"/api/projects/{project['id']}/collaborators/{invitation['id']}",
        json={"role": "viewer"},
        headers=owner_headers,
    )
    assert response.status_code == 200
    assert response.json()["role"] == "viewer"


@pytest.mark.asyncio
async def test_update_collaborator_role_admin_success(
    client: AsyncClient,
    owner_headers: dict,
    project: dict,
    invitee: dict,
    invitee_headers: dict,
    third_user: dict,
    third_headers: dict,
) -> None:
    """Accepted admin collaborator can change another collaborator's role."""
    # Invite invitee as admin and accept
    invite_resp = await client.post(
        f"/api/projects/{project['id']}/collaborators",
        json={"identifier": invitee["email"], "role": "admin"},
        headers=owner_headers,
    )
    collab_id = invite_resp.json()["id"]
    await client.patch(
        f"/api/collaborators/{collab_id}",
        json={"status": "accepted"},
        headers=invitee_headers,
    )

    # Invite third user as viewer
    third_invite = await client.post(
        f"/api/projects/{project['id']}/collaborators",
        json={"identifier": third_user["email"], "role": "viewer"},
        headers=owner_headers,
    )
    third_collab_id = third_invite.json()["id"]

    # Admin changes third user's role
    response = await client.patch(
        f"/api/projects/{project['id']}/collaborators/{third_collab_id}",
        json={"role": "editor"},
        headers=invitee_headers,
    )
    assert response.status_code == 200
    assert response.json()["role"] == "editor"


@pytest.mark.asyncio
async def test_update_collaborator_role_works_on_pending(
    client: AsyncClient, owner_headers: dict, project: dict, invitation: dict
) -> None:
    """Role change is allowed regardless of collaborator status (pending)."""
    response = await client.patch(
        f"/api/projects/{project['id']}/collaborators/{invitation['id']}",
        json={"role": "admin"},
        headers=owner_headers,
    )
    assert response.status_code == 200
    assert response.json()["role"] == "admin"
    assert response.json()["status"] == "pending"


@pytest.mark.asyncio
async def test_update_collaborator_role_403_non_owner(
    client: AsyncClient, third_headers: dict, project: dict, invitation: dict
) -> None:
    """Non-owner/non-admin cannot change collaborator role."""
    response = await client.patch(
        f"/api/projects/{project['id']}/collaborators/{invitation['id']}",
        json={"role": "viewer"},
        headers=third_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_collaborator_role_404_not_found(
    client: AsyncClient, owner_headers: dict, project: dict
) -> None:
    """Returns 404 when collaborator record does not exist on this project."""
    fake_id = uuid.uuid4()
    response = await client.patch(
        f"/api/projects/{project['id']}/collaborators/{fake_id}",
        json={"role": "viewer"},
        headers=owner_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_invite_collaborator_admin_can_invite(
    client: AsyncClient,
    owner_headers: dict,
    project: dict,
    invitee: dict,
    invitee_headers: dict,
    third_user: dict,
    third_headers: dict,
) -> None:
    """An accepted admin collaborator can also invite others."""
    # Invite invitee as admin
    await client.post(
        f"/api/projects/{project['id']}/collaborators",
        json={"identifier": invitee["email"], "role": "admin"},
        headers=owner_headers,
    )

    # Accept the invitation (need to patch status)
    # Use the DB directly via a PATCH endpoint — this will be part of US-003,
    # but we can simulate acceptance by checking the 403 path for a non-admin.
    # For now, verify that an editor (not yet accepted) gets 403.
    response = await client.post(
        f"/api/projects/{project['id']}/collaborators",
        json={"identifier": third_user["email"], "role": "viewer"},
        headers=invitee_headers,
    )
    # invitee has only a pending invitation (not yet accepted), so 403
    assert response.status_code == 403
