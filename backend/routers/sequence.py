import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth.dependencies import get_current_user
from database.session import get_db
from models.project import Project
from models.sequence import Sequence, SequenceBeat, SequenceMeasure
from models.song import Song
from models.user import User
from schemas.sequence import SequenceCreate, SequenceResponse, SequenceUpdate

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


async def _get_sequence_with_measures(
    song_id: uuid.UUID,
    db: AsyncSession,
) -> Sequence | None:
    """Fetch a sequence with eagerly loaded measures and beats."""
    result = await db.execute(
        select(Sequence)
        .where(Sequence.song_id == song_id)
        .options(selectinload(Sequence.measures).selectinload(SequenceMeasure.beats))
    )
    return result.scalar_one_or_none()


@router.get("/songs/{song_id}/sequence", response_model=SequenceResponse)
async def get_sequence(
    song_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Sequence:
    await _get_owned_song(song_id, current_user, db)

    sequence = await _get_sequence_with_measures(song_id, db)
    if not sequence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sequence not found")

    return sequence


@router.post(
    "/songs/{song_id}/sequence",
    response_model=SequenceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_sequence(
    song_id: uuid.UUID,
    data: SequenceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Sequence:
    await _get_owned_song(song_id, current_user, db)

    existing = await db.execute(select(Sequence).where(Sequence.song_id == song_id))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sequence already exists for this song",
        )

    sequence = Sequence(
        song_id=song_id,
        time_signature_numerator=data.time_signature_numerator,
        time_signature_denominator=data.time_signature_denominator,
        measures_per_line=data.measures_per_line,
    )
    db.add(sequence)
    await db.commit()

    sequence = await _get_sequence_with_measures(song_id, db)
    return sequence  # type: ignore[return-value]


@router.put("/songs/{song_id}/sequence", response_model=SequenceResponse)
async def update_sequence(
    song_id: uuid.UUID,
    data: SequenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Sequence:
    await _get_owned_song(song_id, current_user, db)

    result = await db.execute(select(Sequence).where(Sequence.song_id == song_id))
    sequence = result.scalar_one_or_none()
    if not sequence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sequence not found")

    sequence.time_signature_numerator = data.time_signature_numerator
    sequence.time_signature_denominator = data.time_signature_denominator
    sequence.measures_per_line = data.measures_per_line

    # Delete existing beats first (child records), then measures
    await db.execute(
        delete(SequenceBeat).where(
            SequenceBeat.measure_id.in_(
                select(SequenceMeasure.id).where(SequenceMeasure.sequence_id == sequence.id)
            )
        )
    )
    await db.execute(delete(SequenceMeasure).where(SequenceMeasure.sequence_id == sequence.id))

    # Create new measures and beats.
    # SQLAlchemy's default=uuid.uuid4 runs at INSERT time, not at Python object construction,
    # so measure.id would be None if used directly. Generate the UUID explicitly instead.
    for measure_data in data.measures:
        new_measure_id = uuid.uuid4()
        measure = SequenceMeasure(
            id=new_measure_id,
            sequence_id=sequence.id,
            position=measure_data.position,
            repeat_start=measure_data.repeat_start,
            repeat_end=measure_data.repeat_end,
            ending_number=measure_data.ending_number,
        )
        db.add(measure)
        for beat_data in measure_data.beats:
            beat = SequenceBeat(
                measure_id=new_measure_id,
                beat_position=beat_data.beat_position,
                chord_id=beat_data.chord_id,
            )
            db.add(beat)

    await db.commit()

    sequence = await _get_sequence_with_measures(song_id, db)
    return sequence  # type: ignore[return-value]


@router.delete("/songs/{song_id}/sequence", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sequence(
    song_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await _get_owned_song(song_id, current_user, db)

    sequence = await _get_sequence_with_measures(song_id, db)
    if not sequence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sequence not found")

    await db.delete(sequence)
    await db.commit()
