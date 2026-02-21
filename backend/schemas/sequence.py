import uuid
from datetime import datetime

from pydantic import BaseModel


class SequenceBeatResponse(BaseModel):
    id: uuid.UUID
    measure_id: uuid.UUID
    beat_position: int
    chord_id: uuid.UUID | None

    model_config = {"from_attributes": True}


class SequenceMeasureResponse(BaseModel):
    id: uuid.UUID
    sequence_id: uuid.UUID
    position: int
    repeat_start: bool
    repeat_end: bool
    ending_number: int | None
    beats: list[SequenceBeatResponse]

    model_config = {"from_attributes": True}


class SequenceResponse(BaseModel):
    id: uuid.UUID
    song_id: uuid.UUID
    time_signature_numerator: int
    time_signature_denominator: int
    measures_per_line: int
    created_at: datetime
    updated_at: datetime
    measures: list[SequenceMeasureResponse]

    model_config = {"from_attributes": True}


class SequenceCreate(BaseModel):
    time_signature_numerator: int = 4
    time_signature_denominator: int = 4
    measures_per_line: int = 4


class SequenceBeatIn(BaseModel):
    beat_position: int
    chord_id: uuid.UUID | None = None


class SequenceMeasureIn(BaseModel):
    position: int
    repeat_start: bool = False
    repeat_end: bool = False
    ending_number: int | None = None
    beats: list[SequenceBeatIn] = []


class SequenceUpdate(BaseModel):
    time_signature_numerator: int = 4
    time_signature_denominator: int = 4
    measures_per_line: int = 4
    measures: list[SequenceMeasureIn] = []
