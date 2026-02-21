import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Sequence(Base):
    __tablename__ = "sequence"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    song_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("songs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    time_signature_numerator: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    time_signature_denominator: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    measures_per_line: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    song: Mapped["Song"] = relationship(back_populates="sequence")  # noqa: F821
    measures: Mapped[list["SequenceMeasure"]] = relationship(
        back_populates="sequence", cascade="all, delete-orphan", order_by="SequenceMeasure.position"
    )


class SequenceMeasure(Base):
    __tablename__ = "sequence_measure"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sequence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sequence.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    repeat_start: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    repeat_end: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ending_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("sequence_id", "position", name="uq_sequence_measure_position"),
    )

    sequence: Mapped["Sequence"] = relationship(back_populates="measures")
    beats: Mapped[list["SequenceBeat"]] = relationship(
        back_populates="measure",
        cascade="all, delete-orphan",
        order_by="SequenceBeat.beat_position",
    )


class SequenceBeat(Base):
    __tablename__ = "sequence_beat"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    measure_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sequence_measure.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    beat_position: Mapped[int] = mapped_column(Integer, nullable=False)
    chord_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chords.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    measure: Mapped["SequenceMeasure"] = relationship(back_populates="beats")
    chord: Mapped["Chord"] = relationship()  # noqa: F821
