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
    AppointmentUpdate,
    AppointmentResponse,
)
from app.services.appointments import (
    create_appointment,
    update_appointment,
    cancel_appointment,
)


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
)


def check_patient_role(current_user: User):
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can manage appointments",
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
    check_patient_role(current_user)

    try:
        return create_appointment(
            db=db,
            current_user=current_user,
            appointment_data=appointment_data,
        )

    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
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
    check_patient_role(current_user)

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


@router.patch(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
def edit_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_patient_role(current_user)

    try:
        return update_appointment(
            db=db,
            current_user=current_user,
            appointment_id=appointment_id,
            appointment_data=appointment_data,
        )

    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


@router.patch(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponse,
)
def cancel_patient_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_patient_role(current_user)

    try:
        return cancel_appointment(
            db=db,
            current_user=current_user,
            appointment_id=appointment_id,
        )

    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )