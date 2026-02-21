import uuid
from datetime import datetime

from pydantic import BaseModel

from models.collaborator import CollaboratorRole, CollaboratorStatus


class CollaboratorInviteRequest(BaseModel):
    identifier: str
    role: CollaboratorRole


class CollaboratorResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    inviter_id: uuid.UUID
    invitee_id: uuid.UUID
    role: CollaboratorRole
    status: CollaboratorStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
