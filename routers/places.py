import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID

from database import get_db
from models import Place
from request_models.places_model import PlaceCreate
from response_models.places_model import PlaceResponse, PlaceListResponse

router = APIRouter(prefix="/places", tags=["places"])


@router.post("", 
            response_model=PlaceResponse,
            tags=["places"],
            summary="Create Place")
def create_place(place: PlaceCreate, db: Session = Depends(get_db)):
    """
    Create a new place in the database.
    
    The endpoint accepts latitude and longitude and creates a PostGIS geometry point.
    """
    logging.debug(
        "Creating place: name=%s, type_id=%s, parent_id=%s, latitude=%s, longitude=%s",
        place.name,
        place.type_id,
        place.parent_id,
        place.latitude,
        place.longitude,
    )

    try:
        new_place = Place(
            name=place.name,
            type_id=place.type_id,
            parent_id=place.parent_id,
            latitude=place.latitude,
            longitude=place.longitude,
            geom=func.ST_GeomFromText(
                f"POINT({place.longitude} {place.latitude})", 4326
            ),
        )
        db.add(new_place)
        db.commit()
        db.refresh(new_place)

        logging.info(f"Place created successfully: {new_place.id}")
        logging.debug(f"Place created: {new_place}")
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating place: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    return new_place


@router.get(
    "/{place_id}",
    response_model=PlaceResponse,
    tags=["places"],
    summary="Get Place details by ID",
)
def get_place(
    place_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a place by its ID."""

    logging.debug("Fetching place by id: %s", place_id)

    place = (
        db.query(Place)
        .filter(Place.id == place_id)
        .first()
    )

    if place is None:
        logging.debug("Place not found: id=%s", place_id)
        raise HTTPException(
            status_code=404,
            detail="Place not found",
        )

    logging.debug(
        "Place found: id=%s, name=%s, latitude=%s, longitude=%s",
        place.id,
        place.name,
        place.latitude,
        place.longitude,
    )

    logging.debug(f"Place found: {place}")

    return PlaceResponse(
        id=place.id,
        name=place.name,
        latitude=place.latitude,
        longitude=place.longitude,
    )

@router.get("", 
            response_model=list[PlaceListResponse],
            tags=["places"],
            summary="Get List Of Places")
def get_all_places(db: Session = Depends(get_db)):
    """Get all places with id and name only."""
    logging.debug("Fetching all places")

    places = db.query(Place).all()

    logging.debug("Places found: count=%s", len(places))
    logging.debug(f'{places}')

    return [
        PlaceListResponse(
            id=place.id,
            name=place.name,
        )
        for place in places
    ]
