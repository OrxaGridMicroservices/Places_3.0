import logging
from fastapi import FastAPI
from routers.places import router as places_router
from routers.place_types import router as place_types_router, seed_default_place_types
from models import Base
from database import engine, SessionLocal

# Create tables
Base.metadata.create_all(bind=engine)

# Seed default place types (Country, State, City)
with SessionLocal() as db:
    seed_default_place_types(db)

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Include routers
app.include_router(places_router)
app.include_router(place_types_router)
