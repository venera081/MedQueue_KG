from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.doctor import (
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse,
)

from app.services.doctor import (
    create_doctor,
    get_doctors,
    get_doctor_by_id,
    update_doctor,
    delete_doctor,
)


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"],
)


@router.post(
    "/",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_doctor_endpoint(
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db),
):
    doctor, error = create_doctor(db, doctor_data)

    if error == "user_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if error == "user_not_doctor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have DOCTOR role",
        )

    if error == "user_inactive":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive",
        )

    if error == "profile_exists":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Doctor profile already exists",
        )

    if error == "clinic_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinic not found",
        )

    if error == "specialization_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialization not found",
        )

    return doctor


@router.get(
    "/",
    response_model=list[DoctorResponse],
)
def get_doctors_endpoint(
    db: Session = Depends(get_db),
):
    return get_doctors(db)


@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse,
)
def get_doctor_endpoint(
    doctor_id: int,
    db: Session = Depends(get_db),
):
    doctor = get_doctor_by_id(db, doctor_id)

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    return doctor


@router.put(
    "/{doctor_id}",
    response_model=DoctorResponse,
)
def update_doctor_endpoint(
    doctor_id: int,
    doctor_data: DoctorUpdate,
    db: Session = Depends(get_db),
):
    doctor, error = update_doctor(
        db,
        doctor_id,
        doctor_data,
    )

    if error == "doctor_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    if error == "clinic_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinic not found",
        )

    if error == "specialization_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialization not found",
        )

    return doctor


@router.delete(
    "/{doctor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_doctor_endpoint(
    doctor_id: int,
    db: Session = Depends(get_db),
):
    deleted = delete_doctor(db, doctor_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )