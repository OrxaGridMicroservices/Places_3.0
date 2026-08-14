from sqlalchemy import Column, String, Float, Integer, UUID as SQLAlchemy_UUID
from geoalchemy2 import Geometry
import uuid
from database import Base


class Place(Base):
    __tablename__ = "places"

    id = Column(SQLAlchemy_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type_id = Column(SQLAlchemy_UUID(as_uuid=True), nullable=False)
    parent_id = Column(SQLAlchemy_UUID(as_uuid=True), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    # PostGIS geometry column for geographic queries
    geom = Column(Geometry("POINT", srid=4326), nullable=False)


class PlaceType(Base):
    __tablename__ = "place_types"

    id = Column(SQLAlchemy_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    level = Column(Integer, nullable=False)
