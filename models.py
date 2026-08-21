from sqlalchemy import Column, String, ForeignKey
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
import uuid
from database import Base


class Place(Base):
    __tablename__ = "places"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    type_id = Column(String(36), ForeignKey("places_types.id"), nullable=False)
    asset_id = Column(String(36), nullable=True)
    # PostGIS geometry column for geographic queries; latitude/longitude are derived from this
    geom = Column(Geometry("POINT", srid=4326), nullable=False)

    @property
    def latitude(self):
        return to_shape(self.geom).y

    @property
    def longitude(self):
        return to_shape(self.geom).x


class PlaceType(Base):
    __tablename__ = "places_types"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
