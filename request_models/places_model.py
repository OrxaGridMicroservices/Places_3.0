from typing import Optional
from pydantic import BaseModel, Field


class PlaceCreate(BaseModel):
    """Request model for creating a new place."""

    name: str = Field(
        ...,
        description="Name of the place",
        examples=["India"]
    )
    type_id: str = Field(
        ...,
        description="UUID of the place type",
        examples=["00589010-cb58-11f0-ba61-e18b1d833212"]
    )
    asset_id: Optional[str] = Field(
        default=None,
        description="Cross-referenced ID of the corresponding asset in the assets service",
        examples=["00589010-cb58-11f0-ba61-e18b1d833213"]
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
