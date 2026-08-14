import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import PlaceType
from request_models.place_types_model import PlaceTypeCreate
from response_models.place_types_model import (
    PlaceTypeResponse,
    PlaceTypeListResponse,
    PlaceTypeDeleteResponse,
)

router = APIRouter(prefix="/place-types", tags=["place-types"])

DEFAULT_PLACE_TYPES = [
    {"name": "Country", "level": 10},
    {"name": "State", "level": 20},
    {"name": "City", "level": 30},
]


def seed_default_place_types(db: Session):
    """Seed default place types (Country, State, City) if they don't already exist."""

    for default_type in DEFAULT_PLACE_TYPES:
        existing = (
            db.query(PlaceType)
            .filter(PlaceType.name == default_type["name"])
            .first()
        )

        if existing is None:
            db.add(PlaceType(name=default_type["name"], level=default_type["level"]))

    db.commit()


@router.post("",
             response_model=PlaceTypeResponse,
             tags=["place-types"],
             summary="Create Place Type")
def create_place_type(place_type: PlaceTypeCreate, db: Session = Depends(get_db)):
    """Create a new place type in the database."""

    logging.debug(
        "Creating place type: name=%s, level=%s",
        place_type.name,
        place_type.level,
    )

    try:
        new_place_type = PlaceType(
            name=place_type.name,
            level=place_type.level,
        )
        db.add(new_place_type)
        db.commit()
        db.refresh(new_place_type)

        logging.info(f"Place type created successfully: {new_place_type.id}")
        logging.debug(f"Place type created: {new_place_type}")
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating place type: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

    return new_place_type


@router.get(
    "/{id}",
    response_model=PlaceTypeResponse,
    tags=["place-types"],
    summary="Get Place Type details by ID",
)
def get_place_type(
    id: str,
    db: Session = Depends(get_db),
):
    """Get a place type by its ID."""

    logging.debug("Fetching place type by id: %s", id)

    try:
        place_type = (
            db.query(PlaceType)
            .filter(PlaceType.id == id)
            .first()
        )
    except Exception as e:
        logging.error(f"Error fetching place type: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

    if place_type is None:
        logging.debug("Place type not found: id=%s", id)
        raise HTTPException(
            status_code=404,
            detail="Place type not found",
        )

    logging.debug(
        "Place type found: id=%s, name=%s, level=%s",
        place_type.id,
        place_type.name,
        place_type.level,
    )

    return PlaceTypeResponse(
        id=place_type.id,
        name=place_type.name,
        level=place_type.level,
    )


@router.get("",
            response_model=list[PlaceTypeListResponse],
            tags=["place-types"],
            summary="Get List Of Place Types")
def get_all_place_types(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    name: Optional[str] = Query(default=None, description="The case insensitive 'substring' filter"),
):
    """Get all place types."""

    logging.debug(
        "Fetching all place types: page=%s, page_size=%s, name=%s",
        page,
        page_size,
        name,
    )

    try:
        query = db.query(PlaceType)

        if name is not None:
            query = query.filter(PlaceType.name.ilike(f"%{name}%"))

        place_types = (
            query
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
    except Exception as e:
        logging.error(f"Error fetching place types: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

    logging.debug("Place types found: count=%s", len(place_types))

    return [
        PlaceTypeListResponse(
            id=place_type.id,
            name=place_type.name,
            level=place_type.level,
        )
        for place_type in place_types
    ]


@router.put(
    "/{id}",
    response_model=PlaceTypeResponse,
    tags=["place-types"],
    summary="Update Place Type",
)
def update_place_type(
    id: str,
    place_type: PlaceTypeCreate,
    db: Session = Depends(get_db),
):
    """Update an existing place type by its ID."""

    logging.debug(
        "Updating place type: id=%s, name=%s, level=%s",
        id,
        place_type.name,
        place_type.level,
    )

    try:
        existing_place_type = (
            db.query(PlaceType)
            .filter(PlaceType.id == id)
            .first()
        )
    except Exception as e:
        logging.error(f"Error fetching place type: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    if existing_place_type is None:
        logging.debug("Place type not found: id=%s", id)
        raise HTTPException(
            status_code=404,
            detail="Place type not found",
        )

    try:
        existing_place_type.name = place_type.name
        existing_place_type.level = place_type.level
        db.commit()
        db.refresh(existing_place_type)

        logging.info(f"Place type updated successfully: {existing_place_type.id}")
        logging.debug(f"Place type updated: {existing_place_type}")
    except Exception as e:
        db.rollback()
        logging.error(f"Error updating place type: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

    return existing_place_type


@router.delete(
    "/{id}",
    response_model=PlaceTypeDeleteResponse,
    tags=["place-types"],
    summary="Delete Place Type",
)
def delete_place_type(
    id: str,
    db: Session = Depends(get_db),
):
    """Delete a place type by its ID."""

    logging.debug("Deleting place type: id=%s", id)

    try:
        existing_place_type = (
            db.query(PlaceType)
            .filter(PlaceType.id == id)
            .first()
        )
    except Exception as e:
        logging.error(f"Error fetching place type: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    if existing_place_type is None:
        logging.debug("Place type not found: id=%s", id)
        raise HTTPException(
            status_code=404,
            detail="Place type not found",
        )

    try:
        db.delete(existing_place_type)
        db.commit()

        logging.info(f"Place type deleted successfully: {id}")
        logging.debug(f"Place type deleted: {existing_place_type}")
    except Exception as e:
        db.rollback()
        logging.error(f"Error deleting place type: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

    return PlaceTypeDeleteResponse(id=id)
