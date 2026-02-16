"""add starting_fret to chords

Revision ID: 851f7f6990f1
Revises: 8660a237d474
Create Date: 2026-02-16 10:28:45.303233

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "851f7f6990f1"
down_revision: str | None = "8660a237d474"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "chords",
        sa.Column("starting_fret", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("chords", "starting_fret")
