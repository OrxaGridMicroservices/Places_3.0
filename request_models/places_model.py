from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class PlaceCreate(BaseModel):
    """Request model for creating a new place."""
    
    name: str = Field(
        ...,
        description="Name of the place",
        examples=["India"]
    )
    type_id: UUID = Field(
        ...,
        description="UUID of the place type",
        examples=["00589010-cb58-11f0-ba61-e18b1d833212"]
    )
    parent_id: Optional[UUID] = Field(
        None,
        description="UUID of the parent place (for hierarchical places)",
        examples=["014e3ab0-cb58-11f0-ba61-e18b1d833212"]
    )
    latitude: float = Field(
        ...,
        description="Latitude coordinate (WGS84)",
        examples=[15.56878, 40.7128, 48.8566]
    )
    longitude: float = Field(
        ...,
        description="Longitude coordinate (WGS84)",
        examples=[70.5678, -74.0060, 2.2922]
    )
