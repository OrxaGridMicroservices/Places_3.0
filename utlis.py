from sqlalchemy import func
from sqlalchemy.sql.elements import ColumnElement

from request_models.places_model import Coordinate, GeometryData, GeometryType

# https://postgis.net/docs/ST_MakePoint.html
def make_point_geometry(data: Coordinate) -> ColumnElement:
    """
    Create a PostGIS POINT geometry from a single [x, y] coordinate.

    Args:
        data: A coordinate in [x, y] format.

    Returns:
        A SQLAlchemy expression representing a PostGIS POINT.
    """
    return func.ST_MakePoint(
        data[0],
        data[1],
    )

# https://postgis.net/docs/ST_MakeLine.html
def make_linestring_geometry(
    data: list[Coordinate],
) -> ColumnElement:
    """
    Create a PostGIS LINESTRING geometry from a list of [x, y] coordinates.

    Args:
        data: A list of coordinates in [x, y] format.

    Returns:
        A SQLAlchemy expression representing a PostGIS LINESTRING.
    """
    points = [
        func.ST_MakePoint(
            coordinate[0],
            coordinate[1],
        )
        for coordinate in data
    ]

    return func.ST_MakeLine(points)

# https://postgis.net/docs/ST_MakePolygon.html
def make_polygon_geometry(
    data: list[Coordinate],
) -> ColumnElement:
    """
    Create a PostGIS POLYGON geometry from a list of [x, y] coordinates.

    The first and last coordinates must be identical to form a
    closed polygon ring.

    Args:
        data: A list of coordinates in [x, y] format.

    Returns:
        A SQLAlchemy expression representing a PostGIS POLYGON.
    """
    points = [
        func.ST_MakePoint(
            coordinate[0],
            coordinate[1],
        )
        for coordinate in data
    ]

    ring = func.ST_MakeLine(points)

    return func.ST_MakePolygon(ring)


GEOMETRY_BUILDERS = {
    GeometryType.POINT: make_point_geometry,
    GeometryType.LINESTRING: make_linestring_geometry,
    GeometryType.POLYGON: make_polygon_geometry,
}


def build_geometry(
    geometry_type: GeometryType,
    geometry_data: GeometryData,
) -> ColumnElement:
    """
    Build a PostGIS geometry based on the geometry type.

    The appropriate geometry builder is selected from GEOMETRY_BUILDERS.
    The resulting geometry is assigned SRID 4326 (WGS 84).

    Args:
        geometry_type: Type of geometry to create.
        geometry_data: Coordinates used to create the geometry.

    Returns:
        A SQLAlchemy expression representing the PostGIS geometry
        with SRID 4326.
    """
    builder = GEOMETRY_BUILDERS.get(geometry_type)

    if builder is None:
        raise ValueError(
            f"Unsupported geometry type: {geometry_type}"
        )

    geometry = builder(geometry_data)

    return func.ST_SetSRID(
        geometry,
        4326,
    )
