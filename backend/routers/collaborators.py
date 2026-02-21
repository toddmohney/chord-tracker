import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from database.session import get_db
from models.collaborator import CollaboratorRole, CollaboratorStatus, ProjectCollaborator
from models.project import Project
from models.user import User
from schemas.collaborator import CollaboratorInviteRequest, CollaboratorResponse

router = APIRouter()


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
    # Load project
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Check that requester is the owner or an admin collaborator
    is_owner = project.user_id == current_user.id
    if not is_owner:
        collab_result = await db.execute(
            select(ProjectCollaborator).where(
                ProjectCollaborator.project_id == project_id,
                ProjectCollaborator.invitee_id == current_user.id,
                ProjectCollaborator.status == CollaboratorStatus.accepted,
            )
        )
        collab = collab_result.scalar_one_or_none()
        if not collab or collab.role != CollaboratorRole.admin:
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
