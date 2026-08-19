from pydantic import BaseModel, Field, field_validator


class PlaceTypeResponse(BaseModel):
    """Response model for place type data."""

    id: str = Field(
        ...,
        description="Unique identifier of the place type",
        examples=["00589010-cb58-11f0-ba61-e18b1d833212"]
    )

    @field_validator("id", mode="before")
    @classmethod
    def _stringify_id(cls, value):
        return str(value)

    name: str = Field(
        ...,
        description="Name of the place type",
        examples=["Country"]
    )


class PlaceTypeListResponse(BaseModel):
    id: str = Field(
        ...,
        description="Unique identifier of the place type",
        examples=["00589010-cb58-11f0-ba61-e18b1d833212"]
    )
    name: str = Field(
        ...,
        description="Name of the place type",
        examples=["Country"]
    )

    @field_validator("id", mode="before")
    @classmethod
    def _stringify_id(cls, value):
        return str(value)


class PlaceTypeDeleteResponse(BaseModel):
    """Response model for place type deletion."""

    id: str = Field(
        ...,
        description="Result message of the delete operation",
        examples=["00589010-cb58-11f0-ba61-e18b1d833212"]
    )
