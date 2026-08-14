from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class PlaceResponse(BaseModel):
    id: UUID
    name: str
    type_id: UUID
    parent_id: Optional[UUID]
    latitude: float
    longitude: float

    class Config:
        from_attributes = True
