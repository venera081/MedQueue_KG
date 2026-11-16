from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.appointment import Appointment
from app.models.profile import PatientProfile, DoctorProfile
from app.models.schedule import DoctorSchedule
from app.models.enums import AppointmentStatus
from app.models.user import User
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate


def _get_patient(db: Session, user_id: int) -> PatientProfile:
    statement = select(PatientProfile).where(
        PatientProfile.user_id == user_id
    )
    patient = db.scalars(statement).first()

    if patient is None:
        raise LookupError("Patient profile not found")

    return patient


def _get_patient_appointment(
    db: Session,
    patient_id: int,
    appointment_id: int,
) -> Appointment:
    statement = select(Appointment).where(
        Appointment.id == appointment_id,
        Appointment.patient_id == patient_id,
    )
    appointment = db.scalars(statement).first()

    if appointment is None:
        raise LookupError("Appointment not found")

    return appointment


def _calculate_appointment_end(
    db: Session,
    doctor_id: int,
    appointment_date: date,
    start_time,
):
    if appointment_date < date.today():
        raise ValueError("Appointment date cannot be in the past")

    doctor_statement = select(DoctorProfile).where(
        DoctorProfile.id == doctor_id
    )
    doctor = db.scalars(doctor_statement).first()

    if doctor is None:
        raise ValueError("Doctor not found")

    day_of_week = appointment_date.weekday()

    schedule_statement = select(DoctorSchedule).where(
        DoctorSchedule.doctor_id == doctor.id,
        DoctorSchedule.day_of_week == day_of_week,
    )
    schedules = list(db.scalars(schedule_statement).all())

    if not schedules:
        raise ValueError("Doctor does not work on this day")

    for schedule in schedules:
        if start_time < schedule.start_time:
            continue

        appointment_duration = timedelta(
            minutes=schedule.slot_duration
        )

        start_datetime = datetime.combine(
            appointment_date,
            start_time,
        )

        end_datetime = start_datetime + appointment_duration
        calculated_end = end_datetime.time()

        if calculated_end > schedule.end_time:
            continue

        start_minutes = (
            start_time.hour * 60
            + start_time.minute
        )

        schedule_minutes = (
            schedule.start_time.hour * 60
            + schedule.start_time.minute
        )

        difference = start_minutes - schedule_minutes

        if difference % schedule.slot_duration != 0:
            continue

        return calculated_end

    raise ValueError(
        "Selected time is outside the doctor's available slots"
    )


def _check_appointment_conflicts(
    db: Session,
    patient_id: int,
    doctor_id: int,
    appointment_date: date,
    start_time,
    end_time,
    exclude_appointment_id: int | None = None,
):
    doctor_statement = select(Appointment).where(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appointment_date,
        Appointment.status != AppointmentStatus.CANCELLED,
        Appointment.start_time < end_time,
        Appointment.end_time > start_time,
    )

    patient_statement = select(Appointment).where(
        Appointment.patient_id == patient_id,
        Appointment.appointment_date == appointment_date,
        Appointment.status != AppointmentStatus.CANCELLED,
        Appointment.start_time < end_time,
        Appointment.end_time > start_time,
    )

    if exclude_appointment_id is not None:
        doctor_statement = doctor_statement.where(
            Appointment.id != exclude_appointment_id
        )
        patient_statement = patient_statement.where(
            Appointment.id != exclude_appointment_id
        )

    doctor_conflict = db.scalars(doctor_statement).first()

    if doctor_conflict:
        raise ValueError("This appointment slot is already booked")

    patient_conflict = db.scalars(patient_statement).first()

    if patient_conflict:
        raise ValueError(
            "You already have an appointment at this time"
        )


def create_appointment(
    db: Session,
    current_user: User,
    appointment_data: AppointmentCreate,
) -> Appointment:

    patient = _get_patient(db, current_user.id)

    appointment_end = _calculate_appointment_end(
        db=db,
        doctor_id=appointment_data.doctor_id,
        appointment_date=appointment_data.appointment_date,
        start_time=appointment_data.start_time,
    )

    _check_appointment_conflicts(
        db=db,
        patient_id=patient.id,
        doctor_id=appointment_data.doctor_id,
        appointment_date=appointment_data.appointment_date,
        start_time=appointment_data.start_time,
        end_time=appointment_end,
    )

    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=appointment_data.doctor_id,
        appointment_date=appointment_data.appointment_date,
        start_time=appointment_data.start_time,
        end_time=appointment_end,
        status=AppointmentStatus.BOOKED,
    )

    try:
        db.add(appointment)
        db.commit()
        db.refresh(appointment)

    except IntegrityError:
        db.rollback()
        raise ValueError("This appointment slot is already booked")

    except Exception:
        db.rollback()
        raise

    return appointment


def update_appointment(
    db: Session,
    current_user: User,
    appointment_id: int,
    appointment_data: AppointmentUpdate,
) -> Appointment:

    patient = _get_patient(db, current_user.id)

    appointment = _get_patient_appointment(
        db=db,
        patient_id=patient.id,
        appointment_id=appointment_id,
    )

    if appointment.status != AppointmentStatus.BOOKED:
        raise ValueError("Only booked appointments can be updated")

    new_date = (
        appointment_data.appointment_date
        if appointment_data.appointment_date is not None
        else appointment.appointment_date
    )

    new_start_time = (
        appointment_data.start_time
        if appointment_data.start_time is not None
        else appointment.start_time
    )

    new_end_time = _calculate_appointment_end(
        db=db,
        doctor_id=appointment.doctor_id,
        appointment_date=new_date,
        start_time=new_start_time,
    )

    _check_appointment_conflicts(
        db=db,
        patient_id=patient.id,
        doctor_id=appointment.doctor_id,
        appointment_date=new_date,
        start_time=new_start_time,
        end_time=new_end_time,
        exclude_appointment_id=appointment.id,
    )

    appointment.appointment_date = new_date
    appointment.start_time = new_start_time
    appointment.end_time = new_end_time

    try:
        db.commit()
        db.refresh(appointment)

    except IntegrityError:
        db.rollback()
        raise ValueError("This appointment slot is already booked")

    except Exception:
        db.rollback()
        raise

    return appointment


def cancel_appointment(
    db: Session,
    current_user: User,
    appointment_id: int,
) -> Appointment:

    patient = _get_patient(db, current_user.id)

    appointment = _get_patient_appointment(
        db=db,
        patient_id=patient.id,
        appointment_id=appointment_id,
    )

    if appointment.status != AppointmentStatus.BOOKED:
        raise ValueError("Only booked appointments can be cancelled")

    appointment.status = AppointmentStatus.CANCELLED

    db.commit()
    db.refresh(appointment)

    return appointment