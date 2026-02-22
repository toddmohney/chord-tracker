import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator

from models.collaborator import ProjectRole


class ProjectCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            msg = "Project name cannot be empty"
            raise ValueError(msg)
        return v.strip()


class ProjectUpdate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            msg = "Project name cannot be empty"
            raise ValueError(msg)
        return v.strip()


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    user_id: uuid.UUID
    my_role: ProjectRole | None = None
    shared_by: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
