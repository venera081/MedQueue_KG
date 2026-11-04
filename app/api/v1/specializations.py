from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.specialization import (
    SpecializationCreate,
    SpecializationResponse,
)
from app.services.specialization import (
    create_specialization,
    get_specializations,
    get_specialization_by_id,
    update_specialization,
    delete_specialization,
)


router = APIRouter(
    prefix="/specializations",
    tags=["Specializations"],
)


@router.post(
    "/",
    response_model=SpecializationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_specialization_endpoint(
    specialization_data: SpecializationCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_specialization(db, specialization_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/",
    response_model=list[SpecializationResponse],
)
def get_specializations_endpoint(
    db: Session = Depends(get_db),
):
    return get_specializations(db)


@router.get(
    "/{specialization_id}",
    response_model=SpecializationResponse,
)
def get_specialization_endpoint(
    specialization_id: int,
    db: Session = Depends(get_db),
):
    specialization = get_specialization_by_id(db, specialization_id)

    if specialization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialization not found",
        )

    return specialization


@router.put(
    "/{specialization_id}",
    response_model=SpecializationResponse,
)
def update_specialization_endpoint(
    specialization_id: int,
    specialization_data: SpecializationCreate,
    db: Session = Depends(get_db),
):
    try:
        specialization = update_specialization(
            db,
            specialization_id,
            specialization_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if specialization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialization not found",
        )

    return specialization


@router.delete(
    "/{specialization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_specialization_endpoint(
    specialization_id: int,
    db: Session = Depends(get_db),
):
    deleted = delete_specialization(db, specialization_id)

    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialization not found",
        )

    if deleted is False:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete specialization assigned to doctors.",
        )