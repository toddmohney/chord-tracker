import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth.dependencies import get_current_user
from auth.project_access import ProjectRole, check_project_access
from database.session import get_db
from models.collaborator import CollaboratorStatus, ProjectCollaborator
from models.user import User
from schemas.collaborator import (
    CollaboratorInviteRequest,
    CollaboratorResponse,
    CollaboratorRoleUpdateRequest,
    CollaboratorStatusUpdateRequest,
    PendingInvitationResponse,
)

router = APIRouter()
status_router = APIRouter()

_ADMIN_ROLES = {ProjectRole.owner, ProjectRole.admin}


@router.post(
    "/{project_id}/collaborators",
    response_model=CollaboratorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def invite_collaborator(
    project_id: uuid.UUID,
    data: CollaboratorInviteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectCollaborator:
    project, role = await check_project_access(project_id, current_user, db)

    if role not in _ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Look up invitee by email (User model has no username field)
    user_result = await db.execute(select(User).where(User.email == data.identifier))
    invitee = user_result.scalar_one_or_none()
    if not invitee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check for duplicate pending/accepted invitation
    existing_result = await db.execute(
        select(ProjectCollaborator).where(
            ProjectCollaborator.project_id == project_id,
            ProjectCollaborator.invitee_id == invitee.id,
            ProjectCollaborator.status.in_(
                [CollaboratorStatus.pending, CollaboratorStatus.accepted]
            ),
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already has a pending or accepted invitation for this project",
        )

    collaborator = ProjectCollaborator(
        project_id=project_id,
        inviter_id=current_user.id,
        invitee_id=invitee.id,
        role=data.role,
        status=CollaboratorStatus.pending,
    )
    db.add(collaborator)
    await db.commit()
    await db.refresh(collaborator)
    return collaborator


@status_router.patch("/collaborators/{collaborator_id}", response_model=CollaboratorResponse)
async def update_collaborator_status(
    collaborator_id: uuid.UUID,
    data: CollaboratorStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectCollaborator:
    if data.status == CollaboratorStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot transition back to pending",
        )

    result = await db.execute(
        select(ProjectCollaborator).where(ProjectCollaborator.id == collaborator_id)
    )
    collab = result.scalar_one_or_none()
    if not collab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Collaborator not found"
        )

    if collab.invitee_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    collab.status = data.status
    await db.commit()
    await db.refresh(collab)
    return collab


@status_router.get("/collaborators/pending", response_model=list[PendingInvitationResponse])
async def list_pending_invitations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[PendingInvitationResponse]:
    result = await db.execute(
        select(ProjectCollaborator)
        .where(
            ProjectCollaborator.invitee_id == current_user.id,
            ProjectCollaborator.status == CollaboratorStatus.pending,
        )
        .options(
            selectinload(ProjectCollaborator.project),
            selectinload(ProjectCollaborator.inviter),
        )
    )
    collabs = result.scalars().all()
    return [
        PendingInvitationResponse(
            id=c.id,
            project_id=c.project_id,
            project_name=c.project.name,
            inviter_email=c.inviter.email,
            role=c.role,
            status=c.status,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in collabs
    ]


@router.get("/{project_id}/collaborators", response_model=list[CollaboratorResponse])
async def list_collaborators(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ProjectCollaborator]:
    _, role = await check_project_access(project_id, current_user, db)

    if role not in _ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    collab_result = await db.execute(
        select(ProjectCollaborator).where(ProjectCollaborator.project_id == project_id)
    )
    return list(collab_result.scalars().all())


@router.delete(
    "/{project_id}/collaborators/{collaborator_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_collaborator(
    project_id: uuid.UUID,
    collaborator_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    project, role = await check_project_access(project_id, current_user, db)

    if role != ProjectRole.owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    collab_result = await db.execute(
        select(ProjectCollaborator).where(
            ProjectCollaborator.id == collaborator_id,
            ProjectCollaborator.project_id == project_id,
        )
    )
    collab = collab_result.scalar_one_or_none()
    if not collab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Collaborator not found"
        )

    if collab.invitee_id == project.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the project owner",
        )

    await db.delete(collab)
    await db.commit()


@router.patch("/{project_id}/collaborators/{collaborator_id}", response_model=CollaboratorResponse)
async def update_collaborator_role(
    project_id: uuid.UUID,
    collaborator_id: uuid.UUID,
    data: CollaboratorRoleUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectCollaborator:
    _, role = await check_project_access(project_id, current_user, db)

    if role not in _ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    collab_result = await db.execute(
        select(ProjectCollaborator).where(
            ProjectCollaborator.id == collaborator_id,
            ProjectCollaborator.project_id == project_id,
        )
    )
    collab = collab_result.scalar_one_or_none()
    if not collab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Collaborator not found"
        )

    collab.role = data.role
    await db.commit()
    await db.refresh(collab)
    return collab
