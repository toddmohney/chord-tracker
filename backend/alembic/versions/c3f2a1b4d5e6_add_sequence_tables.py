"""add sequence tables

Revision ID: c3f2a1b4d5e6
Revises: 851f7f6990f1
Create Date: 2026-02-21 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3f2a1b4d5e6"
down_revision: str | None = "851f7f6990f1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sequence",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "song_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("songs.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column(
            "time_signature_numerator",
            sa.Integer(),
            nullable=False,
            server_default="4",
        ),
        sa.Column(
            "time_signature_denominator",
            sa.Integer(),
            nullable=False,
            server_default="4",
        ),
        sa.Column(
            "measures_per_line",
            sa.Integer(),
            nullable=False,
            server_default="4",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "sequence_measure",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "sequence_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sequence.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("repeat_start", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("repeat_end", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("ending_number", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("sequence_id", "position", name="uq_sequence_measure_position"),
    )

    op.create_table(
        "sequence_beat",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "measure_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sequence_measure.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("beat_position", sa.Integer(), nullable=False),
        sa.Column(
            "chord_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("chords.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("sequence_beat")
    op.drop_table("sequence_measure")
    op.drop_table("sequence")
