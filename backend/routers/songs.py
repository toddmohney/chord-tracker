import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from auth.project_access import ProjectRole, check_project_access
from database.session import get_db
from models.song import Song
from models.user import User
from schemas.song import SongCreate, SongResponse, SongUpdate

router = APIRouter()

_EDITOR_ROLES = {ProjectRole.owner, ProjectRole.admin, ProjectRole.editor}


async def _get_song_with_role(
    song_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> tuple[Song, ProjectRole]:
    """Fetch a song and determine caller's role on its project."""
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()

    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")

    _, role = await check_project_access(song.project_id, current_user, db)
    return song, role


@router.get("/projects/{project_id}/songs", response_model=list[SongResponse])
async def list_songs(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Song]:
    await check_project_access(project_id, current_user, db)

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
    _, role = await check_project_access(project_id, current_user, db)

    if role not in _EDITOR_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

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
    song, _ = await _get_song_with_role(song_id, current_user, db)
    return song


@router.put("/songs/{song_id}", response_model=SongResponse)
async def update_song(
    song_id: uuid.UUID,
    data: SongUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Song:
    song, role = await _get_song_with_role(song_id, current_user, db)

    if role not in _EDITOR_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

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
    song, role = await _get_song_with_role(song_id, current_user, db)

    if role not in _EDITOR_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    await db.delete(song)
    await db.commit()
