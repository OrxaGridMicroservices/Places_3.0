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
                    f"{place.geometry_type}({place.geometry_data})",  # rebuild WKT from type + raw coordinates
                    4326,
                ),  # Convert WKT to geometry
            )
            .returning(Place)  # Return the inserted Place
        )
        result = db.execute(stmt)

        new_place = result.scalar_one()  # Get the inserted Place
        logging.debug(f'{new_place=}')

        db.commit()  # Save the insert

    except Exception as e:
        db.rollback()  # Undo the insert

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return PlaceResponse(
        id=new_place.id,
        name=new_place.name,
        type_id=new_place.type_id,
        asset_id=new_place.asset_id,
        geometry_type=new_place.geometry_type,
        geometry_data=new_place.geometry_data,
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

    stmt = select(Place)  # Select all places

    if type_id is not None:
        stmt = stmt.where(
            Place.type_id == type_id
        )

    if name is not None:
        stmt = stmt.where(
            Place.name.ilike(f"%{name}%")  # Filter by name
        )

    stmt = (
        stmt
        .offset(page * page_size)  # Skip previous pages
        .limit(page_size)  # Limit the results
    )

    try:
        places = db.scalars(stmt).all()  # Get all Place objects
        logging.debug(f'{places=}')

        response = [
            PlaceListResponse(
                id=place.id,
                name=place.name,
            )  # Return only id and name
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
            .where(Place.id == place_id)  # Find place by ID
        )

        place = db.scalar(stmt)  # Get the Place or None
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
        geometry_type=place.geometry_type,
        geometry_data=place.geometry_data,
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
                geom=func.ST_GeomFromText(
                    f"{place.geometry_type}({place.geometry_data})",  # rebuild WKT from type + raw coordinates
                    4326,
                ),  # Convert WKT to geometry
            )
            .returning(Place)  # Return the updated Place
        )

        result = db.execute(stmt)

        updated_place = result.scalar_one_or_none()  # Get the updated Place
        logging.debug(f'{updated_place=}')

        if updated_place is None:
            db.rollback()

            raise HTTPException(
                status_code=404,
                detail="Place not found",
            )

        db.commit()  # Save the update

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()  # Undo the update

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return PlaceResponse(
        id=updated_place.id,
        name=updated_place.name,
        type_id=updated_place.type_id,
        asset_id=updated_place.asset_id,
        geometry_type=updated_place.geometry_type,
        geometry_data=updated_place.geometry_data,
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
            .returning(Place.id)  # Return the deleted ID
        )

        result = db.execute(stmt)

        deleted_id = result.scalar_one_or_none()  # Get the deleted ID

        if deleted_id is None:
            db.rollback()

            raise HTTPException(
                status_code=404,
                detail="Place not found",
            )

        db.commit()  # Save the delete

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()  # Undo the delete

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return PlaceDeleteResponse(
        id=deleted_id,
    )
