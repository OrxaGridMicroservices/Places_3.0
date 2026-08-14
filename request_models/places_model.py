from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class PlaceCreate(BaseModel):
    name: str
    type_id: UUID
    parent_id: Optional[UUID] = None
    latitude: float
    longitude: float

    class Config:
        from_attributes = True
