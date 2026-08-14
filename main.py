import logging
from fastapi import FastAPI
from routers.places import router as places_router
from models import Base
from database import engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Include routers
app.include_router(places_router)
