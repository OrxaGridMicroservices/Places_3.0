from pydantic import BaseModel, Field


class PlaceTypeCreate(BaseModel):
    """Request model for creating a new place type."""

    name: str = Field(
        ...,
        description="Name of the place type",
        examples=["Country"]
    )
