from sqlalchemy import Column, String, Float, ForeignKey
from geoalchemy2 import Geometry
import uuid
from database import Base


class Place(Base):
    __tablename__ = "places"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    type_id = Column(String(36), ForeignKey("places_types.id"), nullable=False)
    asset_id = Column(String(36), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    # PostGIS geometry column for geographic queries
    geom = Column(Geometry("POINT", srid=4326), nullable=False)


class PlaceType(Base):
    __tablename__ = "places_types"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
