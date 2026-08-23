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
                geom=func.ST_GeomFromText(  # build a PostGIS point from the request's WKT geometry
                    place.geometry,
                    4326,
                ),
            )
            .returning(Place)  # Return the inserted Place
        )
        result = db.execute(stmt)

        new_place = result.scalar_one()  # Get the inserted Place
        logging.debug(f'{new_place=}')

        db.commit()  # persist the insert

    except Exception as e:
        db.rollback()  # undo the failed transaction

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return PlaceResponse(
            id=place.id,
            name=place.name,
            type_id=place.type_id,
            asset_id=place.asset_id,
            latitude=place.latitude,
            longitude=place.longitude,
        )


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

    stmt = select(Place)  # base query over all places

    if type_id is not None:
        stmt = stmt.where(
            Place.type_id == type_id
        )

    if name is not None:
        stmt = stmt.where(
            Place.name.ilike(f"%{name}%")  # case-insensitive substring match on name
        )

    stmt = (
        stmt
        .offset(page * page_size)  
        .limit(page_size)
    )

    try:
        places = db.scalars(stmt).all()  # run the query and unwrap the Place rows
        logging.debug(f'{places=}')

        response = [
            PlaceListResponse(id=place.id, name=place.name)  # trim each row to id/name only
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
            .where(Place.id == place_id)  # look up a single place by primary key
        )

        place = db.scalar(stmt)  # returns the Place row, or None if not found
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

    return PlaceResponse(
            id=place.id,
            name=place.name,
            type_id=place.type_id,
            asset_id=place.asset_id,
            latitude=place.latitude,
            longitude=place.longitude,
        )


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
                geom=func.ST_GeomFromText(  # rebuild the PostGIS point from the new WKT geometry
                    place.geometry,
                    4326,
                ),
            )
            .returning(Place)  # get the updated row back without a second SELECT
        )

        result = db.execute(stmt)

        updated_place = result.scalar_one_or_none()  # None means no row matched place_id
        logging.debug(f'{updated_place=}')

        if updated_place is None:
            db.rollback()

            raise HTTPException(
                status_code=404,
                detail="Place not found",
            )

        db.commit()  # persist the update

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()  # undo the failed transaction

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return PlaceResponse(
            id=place.id,
            name=place.name,
            type_id=place.type_id,
            asset_id=place.asset_id,
            latitude=place.latitude,
            longitude=place.longitude,
        )


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
            .returning(Place.id)  # confirm which row (if any) was deleted
        )

        result = db.execute(stmt)

        deleted_id = result.scalar_one_or_none()  # None means no row matched place_id

        if deleted_id is None:
            db.rollback()

            raise HTTPException(
                status_code=404,
                detail="Place not found",
            )

        db.commit()  # persist the delete

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()  # undo the failed transaction

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return PlaceDeleteResponse(
        id=deleted_id,
    )
