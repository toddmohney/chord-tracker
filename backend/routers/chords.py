import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from database.session import get_db
from models.chord import Chord
from models.project import Project
from models.song import Song
from models.user import User
from schemas.chord import ChordCreate, ChordResponse, ChordUpdate, ReorderRequest

router = APIRouter()


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

    result = await db.execute(select(Project).where(Project.id == song.project_id))
    project = result.scalar_one_or_none()

    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return song


async def _get_owned_chord(
    chord_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> Chord:
    """Fetch a chord and verify ownership through song -> project -> user."""
    result = await db.execute(select(Chord).where(Chord.id == chord_id))
    chord = result.scalar_one_or_none()

    if not chord:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chord not found")

    await _get_owned_song(chord.song_id, current_user, db)
    return chord


@router.get("/songs/{song_id}/chords", response_model=list[ChordResponse])
async def list_chords(
    song_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Chord]:
    await _get_owned_song(song_id, current_user, db)

    result = await db.execute(
        select(Chord).where(Chord.song_id == song_id).order_by(Chord.position)
    )
    return list(result.scalars().all())


@router.post(
    "/songs/{song_id}/chords",
    response_model=ChordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_chord(
    song_id: uuid.UUID,
    data: ChordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Chord:
    await _get_owned_song(song_id, current_user, db)

    # Auto-assign next position
    result = await db.execute(
        select(func.coalesce(func.max(Chord.position), -1)).where(Chord.song_id == song_id)
    )
    next_position = result.scalar() + 1

    markers_data = [m.model_dump() for m in data.markers]
    chord = Chord(
        name=data.name,
        markers=markers_data,
        position=next_position,
        string_count=data.string_count,
        tuning=data.tuning,
        starting_fret=data.starting_fret,
        song_id=song_id,
    )
    db.add(chord)
    await db.commit()
    await db.refresh(chord)
    return chord


@router.put("/chords/{chord_id}", response_model=ChordResponse)
async def update_chord(
    chord_id: uuid.UUID,
    data: ChordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Chord:
    chord = await _get_owned_chord(chord_id, current_user, db)

    if data.name is not None:
        chord.name = data.name
    if data.markers is not None:
        chord.markers = [m.model_dump() for m in data.markers]
    if data.string_count is not None:
        chord.string_count = data.string_count
    if data.tuning is not None:
        chord.tuning = data.tuning
    if data.starting_fret is not None:
        chord.starting_fret = data.starting_fret

    await db.commit()
    await db.refresh(chord)
    return chord


@router.delete("/chords/{chord_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chord(
    chord_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    chord = await _get_owned_chord(chord_id, current_user, db)
    song_id = chord.song_id
    deleted_position = chord.position

    await db.delete(chord)

    # Re-normalize positions for remaining chords
    result = await db.execute(
        select(Chord)
        .where(Chord.song_id == song_id, Chord.position > deleted_position)
        .order_by(Chord.position)
    )
    for c in result.scalars().all():
        c.position -= 1

    await db.commit()


@router.put(
    "/songs/{song_id}/chords/reorder",
    response_model=list[ChordResponse],
)
async def reorder_chords(
    song_id: uuid.UUID,
    data: ReorderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Chord]:
    await _get_owned_song(song_id, current_user, db)

    # Fetch all chords for this song
    result = await db.execute(select(Chord).where(Chord.song_id == song_id))
    chords = {c.id: c for c in result.scalars().all()}

    # Validate that all chord_ids belong to this song
    if set(data.chord_ids) != set(chords.keys()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="chord_ids must contain exactly all chords in the song",
        )

    # Update positions
    for position, chord_id in enumerate(data.chord_ids):
        chords[chord_id].position = position

    await db.commit()

    # Return in new order
    result = await db.execute(
        select(Chord).where(Chord.song_id == song_id).order_by(Chord.position)
    )
    return list(result.scalars().all())
