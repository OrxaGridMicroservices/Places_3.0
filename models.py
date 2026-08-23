import uuid
from typing import Optional

from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Place(Base):
    __tablename__ = "places"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), unique=True)
    type_id: Mapped[str] = mapped_column(String(36), ForeignKey("places_types.id"))
    asset_id: Mapped[Optional[str]] = mapped_column(String(36))
    # PostGIS geometry column; not restricted to POINT so polygon shapes (e.g. zip code boundaries) can be stored too
    geom: Mapped[WKBElement] = mapped_column(Geometry(srid=4326))

    @property
    def geometry_type(self) -> str:
        # WKT type keyword of the stored shape, e.g. "POINT" or "POLYGON"
        return to_shape(self.geom).geom_type.upper()

    @property
    def geometry_data(self) -> str:
        # raw WKT coordinate content with the outer type wrapper stripped off
        wkt = to_shape(self.geom).wkt
        return wkt[wkt.index("(") + 1 : -1]


class PlaceType(Base):
    __tablename__ = "places_types"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), unique=True)
