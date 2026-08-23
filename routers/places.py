import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.orm import Session

from database import get_db
from models import Place
from request_models.places_model import PlaceCreate
from response_models.places_model import (
    PlaceResponse,
    PlaceListResponse,
    PlaceDeleteResponse,
)


router = APIRouter(
    prefix="/places",
    tags=["places"],
)

@router.post(
    "",
    response_model=PlaceResponse,
    response_model_exclude_none=True,
    tags=["places"],
    summary="Create Place",
)
def create_place(
    place: PlaceCreate,
    db: Session = Depends(get_db),
):
    """Create a new place."""
    try:
        stmt = (
            insert(Place)
            .values(
                name=place.name,
                type_id=place.type_id,
                asset_id=place.asset_id,
                geom=func.ST_GeomFromText(
                    place.geometry,
                    4326,
                ),
            )
            .returning(Place) # add in comments returring featire works
        )
        result = db.execute(stmt)

        new_place = result.scalar_one()  # add commentfor scalar_one()
        logging.debug(f'{new_place=}')

        db.commit()

        logging.info(
            "Place created successfully: id=%s",
            new_place.id,
        )

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    
    return new_place  # return with responces model

@router.get(
    "",
    response_model=list[PlaceListResponse],
    summary="Get List Of Places",
)
def get_all_places(
    db: Session = Depends(get_db),
    page: int = Query(
        0,
        ge=0,
        description="Page number",
    ),
    page_size: int = Query(
        10,
        ge=1,
        le=100,
        description="Number of items per page",
    ),
    type_id: Optional[str] = Query(
        None,
        description="Filter places by type_id",
    ),
    name: Optional[str] = Query(
        None,
        description="Case insensitive substring filter",
    ),
):
    """Get paginated list of places."""

    stmt = select(Place)

    if type_id is not None:
        stmt = stmt.where(
            Place.type_id == type_id
        )

    if name is not None:
        stmt = stmt.where(
            Place.name.ilike(f"%{name}%")
        )

    stmt = (
        stmt
        .offset(page * page_size)
        .limit(page_size)
    )

    try:
        places = db.scalars(stmt).all()
        logging.debug(f'{places=}')

        response = [
            PlaceListResponse(id=place.id, name=place.name)
            for place in places
        ]

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return response


@router.get(
    "/{place_id}",
    response_model=PlaceResponse,
    response_model_exclude_none=True,
    summary="Get Place details by ID",
)
def get_place(
    place_id: str,
    db: Session = Depends(get_db),
):
    """Get a place by its ID."""

    try:
        stmt = (
            select(Place)
            .where(Place.id == place_id)
        )

        place = db.scalar(stmt)
        logging.debug(f'{place=}')

    except Exception as e:
    
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    if place is None:
        raise HTTPException(
            status_code=404,
            detail="Place not found",
        )

    return place


@router.put(
    "/{place_id}",
    response_model=PlaceResponse,
    response_model_exclude_none=True,
    summary="Update Place",
)
def update_place(
    place_id: str,
    place: PlaceCreate,
    db: Session = Depends(get_db),
):
    """Update an existing place."""

    try:
        stmt = (
            update(Place)
            .where(Place.id == place_id)
            .values(
                name=place.name,
                type_id=place.type_id,
                asset_id=place.asset_id,
                geom=func.ST_GeomFromText(
                    place.geometry,
                    4326,
                ),
            )
            .returning(Place)
        )

        result = db.execute(stmt)

        updated_place = result.scalar_one_or_none()
        logging.debug(f'{updated_place=}')

        if updated_place is None:
            db.rollback()

            raise HTTPException(
                status_code=404,
                detail="Place not found",
            )

        db.commit()

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    
    return updated_place


@router.delete(
    "/{place_id}",
    response_model=PlaceDeleteResponse,
    summary="Delete Place",
)
def delete_place(
    place_id: str,
    db: Session = Depends(get_db),
):
    """Delete an existing place."""
    try:
        stmt = (
            delete(Place)
            .where(Place.id == place_id)
            .returning(Place.id)
        )

        result = db.execute(stmt)

        deleted_id = result.scalar_one_or_none()

        if deleted_id is None:
            db.rollback()

            raise HTTPException(
                status_code=404,
                detail="Place not found",
            )

        db.commit()

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return PlaceDeleteResponse(
                id=deleted_id,
            )
