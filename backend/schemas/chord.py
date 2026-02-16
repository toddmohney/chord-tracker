import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class MarkerSchema(BaseModel):
    string: int
    fret: int


class ChordCreate(BaseModel):
    name: str | None = None
    markers: list[MarkerSchema] = Field(default_factory=list)
    string_count: int = 6
    tuning: str = "EADGBE"
    starting_fret: int = 0


class ChordUpdate(BaseModel):
    name: str | None = None
    markers: list[MarkerSchema] | None = None
    string_count: int | None = None
    tuning: str | None = None
    starting_fret: int | None = None


class ChordResponse(BaseModel):
    id: uuid.UUID
    name: str | None
    markers: list[MarkerSchema]
    position: int
    string_count: int
    tuning: str
    starting_fret: int
    song_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReorderRequest(BaseModel):
    chord_ids: list[uuid.UUID]
