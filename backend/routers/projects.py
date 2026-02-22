import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from auth.project_access import ProjectRole, check_project_access, get_project_access
from database.session import get_db
from models.collaborator import CollaboratorStatus, ProjectCollaborator
from models.project import Project
from models.user import User
from schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter()


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ProjectResponse]:
    # Owned projects
    owned_result = await db.execute(
        select(Project)
        .where(Project.user_id == current_user.id)
        .order_by(Project.updated_at.desc())
    )
    owned_projects = owned_result.scalars().all()

    # Collaborated projects (accepted only) — join inviter User for shared_by email
    collab_result = await db.execute(
        select(ProjectCollaborator, Project, User)
        .join(Project, Project.id == ProjectCollaborator.project_id)
        .join(User, User.id == ProjectCollaborator.inviter_id)
        .where(
            ProjectCollaborator.invitee_id == current_user.id,
            ProjectCollaborator.status == CollaboratorStatus.accepted,
        )
    )
    collab_rows = collab_result.all()

    responses: list[ProjectResponse] = []
    for p in owned_projects:
        responses.append(
            ProjectResponse.model_validate(p).model_copy(update={"my_role": ProjectRole.owner})
        )
    for collab, p, inviter in collab_rows:
        responses.append(
            ProjectResponse.model_validate(p).model_copy(
                update={"my_role": ProjectRole(collab.role), "shared_by": inviter.email}
            )
        )

    responses.sort(key=lambda r: r.updated_at, reverse=True)
    return responses


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    project = Project(name=data.name, user_id=current_user.id)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return ProjectResponse.model_validate(project).model_copy(
        update={"my_role": ProjectRole.owner}
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_access: tuple = Depends(get_project_access),
) -> ProjectResponse:
    project, role = project_access
    return ProjectResponse.model_validate(project).model_copy(update={"my_role": role})


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    project, role = await check_project_access(project_id, current_user, db)

    if role != ProjectRole.owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    project.name = data.name
    await db.commit()
    await db.refresh(project)
    return ProjectResponse.model_validate(project).model_copy(update={"my_role": role})


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    project, role = await check_project_access(project_id, current_user, db)

    if role != ProjectRole.owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    await db.delete(project)
    await db.commit()
