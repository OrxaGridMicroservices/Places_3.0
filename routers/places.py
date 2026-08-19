import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import Place
from request_models.places_model import PlaceCreate
from response_models.places_model import PlaceResponse, PlaceListResponse, PlaceDeleteResponse

router = APIRouter(prefix="/places", tags=["places"])


@router.post("", 
            response_model=PlaceResponse,
            response_model_exclude_none=True,
            tags=["places"],
            summary="Create Place")
def create_place(place: PlaceCreate, db: Session = Depends(get_db)):
    """
    Create a new place in the database.
    
    The endpoint accepts latitude and longitude and creates a PostGIS geometry point.
    """
    logging.debug(
        "Creating place: name=%s, type_id=%s, latitude=%s, longitude=%s",
        place.name,
        place.type_id,
        place.latitude,
        place.longitude,
    )

    try:
        new_place = Place(
            name=place.name,
            type_id=place.type_id,
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
    finally:
        db.close()

    return new_place


@router.get(
    "/{place_id}",
    response_model=PlaceResponse,
    response_model_exclude_none=True,
    tags=["places"],
    summary="Get Place details by ID",
)
def get_place(
    place_id: str,
    db: Session = Depends(get_db),
):
    """Get a place by its ID."""

    logging.debug("Fetching place by id: %s", place_id)

    try:
        place = (
            db.query(Place)
            .filter(Place.id == place_id)
            .first()
        )
    except Exception as e:
        logging.error(f"Error fetching place: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

    if place is None:
        logging.debug("Place not found: id=%s", place_id)
        raise HTTPException(
            status_code=404,
            detail="Place not found",
        )

    logging.debug(
        "Place found: id=%s, name=%s, type_id=%s, latitude=%s, longitude=%s",
        place.id,
        place.name,
        place.type_id,
        place.latitude,
        place.longitude,
    )

    return PlaceResponse(
        id=place.id,
        name=place.name,
        type_id=place.type_id,
        latitude=place.latitude,
        longitude=place.longitude,
    )

@router.get("", 
            response_model=list[PlaceListResponse],
            tags=["places"],
            summary="Get List Of Places")
def get_all_places(
    db: Session = Depends(get_db),
    page: int = Query(0, ge=0, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    type_id: Optional[str] = Query(None, description="Filter places by type_id"),
    name: Optional[str] = Query(default=None, description="The case insensitive 'substring' filter")
):
    """Get all places with id and name only."""
    logging.debug(
        "Fetching all places: page=%s, page_size=%s, type_id=%s",
        page,
        page_size,
        type_id,
    )

    try:
        query = db.query(Place)

        if type_id is not None:
            query = query.filter(Place.type_id == type_id)

        if name is not None:
            query = query.filter(Place.name.ilike(f"%{name}%"))

        places = (
            query
            .offset(page * page_size)
            .limit(page_size)
            .all()
        )
    except Exception as e:
        logging.error(f"Error fetching places: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

    logging.debug("Places found: count=%s", len(places))
    logging.debug(f'{places}')

    return [
        PlaceListResponse(
            id=place.id,
            name=place.name,
        )
        for place in places
    ]


@router.put(
    "/{place_id}",
    response_model=PlaceResponse,
    response_model_exclude_none=True,
    tags=["places"],
    summary="Update Place",
)
def update_place(
    place_id: str,
    place: PlaceCreate,
    db: Session = Depends(get_db),
):
    """Update an existing place by its ID."""

    logging.debug(
        "Updating place: id=%s, name=%s, type_id=%s, latitude=%s, longitude=%s",
        place_id,
        place.name,
        place.type_id,
        place.latitude,
        place.longitude,
    )

    try:
        existing_place = (
            db.query(Place)
            .filter(Place.id == place_id)
            .first()
        )
    except Exception as e:
        logging.error(f"Error fetching place: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    if existing_place is None:
        logging.debug("Place not found: id=%s", place_id)
        raise HTTPException(
            status_code=404,
            detail="Place not found",
        )

    try:
        existing_place.name = place.name
        existing_place.type_id = place.type_id
        existing_place.latitude = place.latitude
        existing_place.longitude = place.longitude
        existing_place.geom = func.ST_GeomFromText(
            f"POINT({place.longitude} {place.latitude})", 4326
        )
        db.commit()
        db.refresh(existing_place)

        logging.info(f"Place updated successfully: {existing_place.id}")
        logging.debug(f"Place updated: {existing_place}")
    except Exception as e:
        db.rollback()
        logging.error(f"Error updating place: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

    return existing_place


@router.delete(
    "/{place_id}",
    response_model=PlaceDeleteResponse,
    tags=["places"],
    summary="Delete Place",
)
def delete_place(
    place_id: str,
    db: Session = Depends(get_db),
):
    """Delete a place by its ID."""

    logging.debug("Deleting place: id=%s", place_id)

    try:
        existing_place = (
            db.query(Place)
            .filter(Place.id == place_id)
            .first()
        )
    except Exception as e:
        logging.error(f"Error fetching place: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    try:
        db.delete(existing_place)
        db.commit()

        logging.info(f"Place deleted successfully: {place_id}")
        logging.debug(f"Place deleted: {existing_place}")
    except Exception as e:
        db.rollback()
        logging.error(f"Error deleting place: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

    return PlaceDeleteResponse(id=place_id)
