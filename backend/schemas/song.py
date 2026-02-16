import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator


class SongCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            msg = "Song name cannot be empty"
            raise ValueError(msg)
        return v.strip()


class SongUpdate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            msg = "Song name cannot be empty"
            raise ValueError(msg)
        return v.strip()


class SongResponse(BaseModel):
    id: uuid.UUID
    name: str
    project_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
