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
    # PostGIS geometry column for geographic queries; latitude/longitude are derived from this
    geom: Mapped[WKBElement] = mapped_column(Geometry("POINT", srid=4326))

    @property
    def latitude(self) -> float:
        return to_shape(self.geom).y

    @property
    def longitude(self) -> float:
        return to_shape(self.geom).x


class PlaceType(Base):
    __tablename__ = "places_types"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), unique=True)
