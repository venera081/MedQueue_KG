from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.profile import PatientProfile
from app.models.appointment import Appointment
from app.models.enums import UserRole
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
)
from app.services.appointments import create_appointment


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
)


@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def book_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can book appointments",
        )

    try:
        return create_appointment(
            db=db,
            current_user=current_user,
            appointment_data=appointment_data,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


@router.get(
    "/my",
    response_model=list[AppointmentResponse],
)
def get_my_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can view their appointments",
        )

    patient_statement = select(PatientProfile).where(
        PatientProfile.user_id == current_user.id
    )
    patient = db.scalars(patient_statement).first()

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found",
        )

    statement = (
        select(Appointment)
        .where(Appointment.patient_id == patient.id)
        .order_by(
            Appointment.appointment_date,
            Appointment.start_time,
        )
    )

    return list(db.scalars(statement).all())