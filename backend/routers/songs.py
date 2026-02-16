import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from database.session import get_db
from models.project import Project
from models.song import Song
from models.user import User
from schemas.song import SongCreate, SongResponse, SongUpdate

router = APIRouter()


async def _get_owned_project(
    project_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> Project:
    """Fetch a project and verify the current user owns it."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return project


async def _get_owned_song(
    song_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> Song:
    """Fetch a song and verify ownership through its project."""
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()

    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")

    # Validate ownership through the project
    result = await db.execute(select(Project).where(Project.id == song.project_id))
    project = result.scalar_one_or_none()

    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return song


@router.get("/projects/{project_id}/songs", response_model=list[SongResponse])
async def list_songs(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Song]:
    await _get_owned_project(project_id, current_user, db)

    result = await db.execute(
        select(Song).where(Song.project_id == project_id).order_by(Song.updated_at.desc())
    )
    return list(result.scalars().all())


@router.post(
    "/projects/{project_id}/songs",
    response_model=SongResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_song(
    project_id: uuid.UUID,
    data: SongCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Song:
    await _get_owned_project(project_id, current_user, db)

    song = Song(name=data.name, project_id=project_id)
    db.add(song)
    await db.commit()
    await db.refresh(song)
    return song


@router.get("/songs/{song_id}", response_model=SongResponse)
async def get_song(
    song_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Song:
    return await _get_owned_song(song_id, current_user, db)


@router.put("/songs/{song_id}", response_model=SongResponse)
async def update_song(
    song_id: uuid.UUID,
    data: SongUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Song:
    song = await _get_owned_song(song_id, current_user, db)
    song.name = data.name
    await db.commit()
    await db.refresh(song)
    return song


@router.delete("/songs/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_song(
    song_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    song = await _get_owned_song(song_id, current_user, db)
    await db.delete(song)
    await db.commit()
