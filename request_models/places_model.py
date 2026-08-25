from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field, model_validator


class GeometryType(str, Enum):
    POINT = "POINT"
    LINESTRING = "LINESTRING"
    POLYGON = "POLYGON"


Coordinate = List[float]
GeometryData = Union[Coordinate, List[Coordinate]]

class PlaceCreate(BaseModel):
    """Request model for creating a new place."""

    name: str = Field(
        ...,
        description="Name of the place",
        examples=["India"]
    )
    type_id: str = Field(
        ...,
        description="place type id",
        examples=["00589010-cb58-11f0-ba61-e18b1d833212"],
    )
    asset_id: Optional[str] = Field(
        default=None,
        description="Cross-referenced ID of the corresponding asset",
        examples=["00589010-cb58-11f0-ba61-e18b1d833213"],
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
        ),
        examples=[
            [77.5946, 12.9716],
            [
                [77.5, 12.9],
                [77.6, 12.9],
                [77.6, 13.0],
                [77.5, 12.9],
            ],
        ],
    )

    @model_validator(mode="after")
    def validate_geometry_data(self):
        data = self.geometry_data

        if self.geometry_type == GeometryType.POINT:
            if (
                not isinstance(data, list)
                or len(data) != 2
                or not all(isinstance(value, (int, float)) for value in data)
            ):
                raise ValueError(
                    "POINT geometry_data must be a single [x, y] coordinate"
                )

            return self

        if (
            not isinstance(data, list)
            or not all(
                isinstance(point, list)
                and len(point) == 2
                and all(isinstance(value, (int, float)) for value in point)
                for point in data
            )
        ):
            raise ValueError(
                f"{self.geometry_type.value} geometry_data "
                "must be a list of [x, y] coordinates"
            )

        min_points = (
            4
            if self.geometry_type == GeometryType.POLYGON
            else 2
        )

        if len(data) < min_points:
            raise ValueError(
                f"{self.geometry_type.value} geometry_data "
                f"must contain at least {min_points} coordinates"
            )

        if (
            self.geometry_type == GeometryType.POLYGON
            and data[0] != data[-1]
        ):
            raise ValueError(
                "POLYGON geometry_data must be a closed ring "
                "(first and last coordinates must be equal)"
            )

        return self
