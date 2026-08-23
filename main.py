import logging

from fastapi import FastAPI

from database import engine, SessionLocal
from models import Base

from routers.places import router as places_router
from routers.places_types import (
    router as places_types_router,
    seed_default_place_types,
)

# Create tables
Base.metadata.create_all(engine)

# Seed default place types (Country, State, City)
with SessionLocal() as db:
    seed_default_place_types(db)

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Include routers
app.include_router(places_types_router)
app.include_router(places_router)
