from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.clinic import ClinicCreate, ClinicResponse
from app.services.clinic import (
    create_clinic,
    get_clinics,
    get_clinic_by_id,
    update_clinic,
    delete_clinic,
)

router = APIRouter(
    prefix="/clinics",
    tags=["Clinics"],
)


@router.post(
    "/",
    response_model=ClinicResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_clinic_endpoint(
    clinic_data: ClinicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    return create_clinic(db, clinic_data)


@router.get(
    "/",
    response_model=list[ClinicResponse],
)
def get_clinics_endpoint(
    db: Session = Depends(get_db),
):
    return get_clinics(db)


@router.get(
    "/{clinic_id}",
    response_model=ClinicResponse,
)
def get_clinic_endpoint(
    clinic_id: int,
    db: Session = Depends(get_db),
):
    clinic = get_clinic_by_id(db, clinic_id)

    if clinic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinic not found",
        )

    return clinic


@router.put(
    "/{clinic_id}",
    response_model=ClinicResponse,
)
def update_clinic_endpoint(
    clinic_id: int,
    clinic_data: ClinicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    clinic = update_clinic(db, clinic_id, clinic_data)

    if clinic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinic not found",
        )

    return clinic


@router.delete(
    "/{clinic_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_clinic_endpoint(
    clinic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    deleted = delete_clinic(db, clinic_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinic not found",
        )