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
    geometry_type: str = Field(
        ...,
        description="WKT geometry type keyword",
        examples=["POINT", "POLYGON"]
    )
    geometry_data: str = Field(
        ...,
        description="Raw WKT coordinate content without the type wrapper, e.g. a point's 'x y' or a polygon's '(x y, x y, ...)' ring",
        examples=["77.5946 12.9716", "(77.5 12.9, 77.6 12.9, 77.6 13.0, 77.5 12.9)"]
    )
