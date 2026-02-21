import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class CollaboratorRole(StrEnum):
    viewer = "viewer"
    editor = "editor"
    admin = "admin"


class CollaboratorStatus(StrEnum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"


class ProjectCollaborator(Base):
    __tablename__ = "project_collaborators"
    __table_args__ = (UniqueConstraint("project_id", "invitee_id", name="uq_project_collaborator"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    inviter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    invitee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    role: Mapped[CollaboratorRole] = mapped_column(
        Enum(CollaboratorRole, name="collaborator_role"), nullable=False
    )
    status: Mapped[CollaboratorStatus] = mapped_column(
        Enum(CollaboratorStatus, name="collaborator_status"),
        nullable=False,
        server_default="pending",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    project: Mapped["Project"] = relationship(back_populates="collaborators")  # noqa: F821
    inviter: Mapped["User"] = relationship(foreign_keys=[inviter_id])  # noqa: F821
    invitee: Mapped["User"] = relationship(foreign_keys=[invitee_id])  # noqa: F821
