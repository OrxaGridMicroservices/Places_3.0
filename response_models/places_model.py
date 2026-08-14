from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from typing import List, Optional


class PlaceResponse(BaseModel):
    """Response model for place data."""

    id: str = Field(
        ...,
        description="Unique identifier of the place",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    @field_validator("id", mode="before")
    @classmethod
    def _stringify_id(cls, value):
        return str(value)
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

class PlaceListResponse(BaseModel):
    id: str = Field(
        ...,
        description="Unique identifier of the place",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    name: str = Field(
        ...,
        description="Name of the place",
        examples=["MP", "Central Park", "Eiffel Tower"]
    )

    @field_validator("id", mode="before")
    @classmethod
    def _stringify_id(cls, value):
        return str(value)

class PlaceDeleteResponse(BaseModel):
    """Response model for place deletion."""

    id: str = Field(
        ...,
        description="Result message of the delete operation",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )


class PlaceDescendantItem(BaseModel):
    id: str = Field(
            ...,
            description="Unique identifier of the place",
            examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
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


class PlaceDescendantsResponse(BaseModel):
    descendants: List[PlaceDescendantItem]
