from pydantic import BaseModel, Field
from typing import Optional

from request_models.places_model import GeometryData, GeometryType


class PlaceResponse(BaseModel):
    """Response model for place data."""

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
    geometry_type: GeometryType = Field(
            ...,
            description="Type of geometry",
            examples=["POINT"],
    )
    
    geometry_data: GeometryData = Field(
            ...,
            description=(
                "Coordinates matching geometry_type: "
                "a single [x, y] pair for POINT, "
                "or a list of [x, y] pairs for LINESTRING/POLYGON"
            )
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

class PlaceDeleteResponse(BaseModel):
    """Response model for place deletion."""

    id: str = Field(
        ...,
        description="Result message of the delete operation",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
