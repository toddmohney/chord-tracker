"""Reusable project access dependency for role-based permissions."""

import uuid

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from database.session import get_db
from models.collaborator import CollaboratorStatus, ProjectCollaborator, ProjectRole
from models.project import Project
from models.user import User


async def check_project_access(
    project_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> tuple[Project, ProjectRole]:
    """Return (project, role) for the current user or raise 403/404."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if project.user_id == current_user.id:
        return project, ProjectRole.owner

    collab_result = await db.execute(
        select(ProjectCollaborator).where(
            ProjectCollaborator.project_id == project_id,
            ProjectCollaborator.invitee_id == current_user.id,
            ProjectCollaborator.status == CollaboratorStatus.accepted,
        )
    )
    collab = collab_result.scalar_one_or_none()
    if not collab:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return project, ProjectRole(collab.role)


async def get_project_access(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> tuple[Project, ProjectRole]:
    """FastAPI dependency: returns (project, role) or raises 403/404."""
    return await check_project_access(project_id, current_user, db)
