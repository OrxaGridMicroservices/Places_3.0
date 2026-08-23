import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session

from database import get_db
from models import PlaceType
from request_models.place_types_model import PlaceTypeCreate
from response_models.place_types_model import (
    PlaceTypeResponse,
    PlaceTypeListResponse,
    PlaceTypeDeleteResponse,
)

router = APIRouter(prefix="/places/types", tags=["place/types"])

DEFAULT_PLACE_TYPES = [
    {"name": "Country"},
    {"name": "State"},
    {"name": "City"},
    {"name": "asset"},
]

def seed_default_place_types(db: Session):
    """Seed default place types (Country, State, City, asset) if the table is empty."""

    table_has_data = db.scalar(select(PlaceType.id).limit(1)) is not None

    if table_has_data:
        return

    db.execute(insert(PlaceType), DEFAULT_PLACE_TYPES)
    db.commit()


@router.post("",
             response_model=PlaceTypeResponse,
             tags=["place/types"],
             summary="Create Place Type")
def create_place_type(place_type: PlaceTypeCreate, db: Session = Depends(get_db)):
    """Create a new place type in the database."""

    logging.debug(
        "Creating place type: name=%s",
        place_type.name,
    )

    try:
        stmt = (
            insert(PlaceType)
            .values(name=place_type.name)
            .returning(PlaceType)
        )
        new_place_type = db.execute(stmt).scalar_one()

        db.commit()

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
    tags=["place/types"],
    summary="Get Place Type details by ID",
)
def get_place_type(
    id: str,
    db: Session = Depends(get_db),
):
    """Get a place type by its ID."""

    logging.debug("Fetching place type by id: %s", id)

    try:
        place_type = db.scalar(
            select(PlaceType).where(PlaceType.id == id)
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
        "Place type found: id=%s, name=%s",
        place_type.id,
        place_type.name,
    )

    return PlaceTypeResponse(
        id=place_type.id,
        name=place_type.name,
    )


@router.get("",
            response_model=list[PlaceTypeListResponse],
            tags=["place/types"],
            summary="Get List Of Place Types")
def get_all_place_types(
    db: Session = Depends(get_db),
    page: int = Query(0, ge=0, description="Page number"),
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
        stmt = select(PlaceType)

        if name is not None:
            stmt = stmt.where(PlaceType.name.ilike(f"%{name}%"))

        stmt = stmt.offset(page * page_size).limit(page_size)

        place_types = db.scalars(stmt).all()
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
        )
        for place_type in place_types
    ]


@router.put(
    "/{id}",
    response_model=PlaceTypeResponse,
    tags=["place/types"],
    summary="Update Place Type",
)
def update_place_type(
    id: str,
    place_type: PlaceTypeCreate,
    db: Session = Depends(get_db),
):
    """Update an existing place type by its ID."""

    logging.debug(
        "Updating place type: id=%s, name=%s",
        id,
        place_type.name,
    )

    try:
        stmt = (
            update(PlaceType)
            .where(PlaceType.id == id)
            .values(name=place_type.name)
            .returning(PlaceType)
        )
        updated_place_type = db.execute(stmt).scalar_one_or_none()

        if updated_place_type is None:
            db.rollback()

            logging.debug("Place type not found: id=%s", id)
            raise HTTPException(
                status_code=404,
                detail="Place type not found",
            )

        db.commit()

        logging.info(f"Place type updated successfully: {updated_place_type.id}")
        logging.debug(f"Place type updated: {updated_place_type}")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Error updating place type: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

    return updated_place_type


@router.delete(
    "/{id}",
    response_model=PlaceTypeDeleteResponse,
    tags=["place/types"],
    summary="Delete Place Type",
)
def delete_place_type(
    id: str,
    db: Session = Depends(get_db),
):
    """Delete a place type by its ID."""

    logging.debug("Deleting place type: id=%s", id)

    try:
        stmt = (
            delete(PlaceType)
            .where(PlaceType.id == id)
            .returning(PlaceType.id)
        )
        deleted_id = db.execute(stmt).scalar_one_or_none()

        if deleted_id is None:
            db.rollback()

            logging.debug("Place type not found: id=%s", id)
            raise HTTPException(
                status_code=404,
                detail="Place type not found",
            )

        db.commit()

        logging.info(f"Place type deleted successfully: {deleted_id}")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Error deleting place type: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

    return PlaceTypeDeleteResponse(id=deleted_id)
