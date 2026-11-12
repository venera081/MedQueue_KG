from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.appointment import Appointment
from app.models.profile import PatientProfile, DoctorProfile
from app.models.schedule import DoctorSchedule
from app.models.enums import AppointmentStatus
from app.models.user import User
from app.schemas.appointment import AppointmentCreate


def create_appointment(
    db: Session,
    current_user: User,
    appointment_data: AppointmentCreate,
) -> Appointment:

    # 1. Проверяем, что дата не в прошлом.
    if appointment_data.appointment_date < date.today():
        raise ValueError("Appointment date cannot be in the past")

    # 2. Получаем профиль пациента по текущему пользователю.
    patient_statement = select(PatientProfile).where(
        PatientProfile.user_id == current_user.id
    )
    patient = db.scalars(patient_statement).first()

    if patient is None:
        raise ValueError("Patient profile not found")

    # 3. Проверяем существование врача.
    doctor_statement = select(DoctorProfile).where(
        DoctorProfile.id == appointment_data.doctor_id
    )
    doctor = db.scalars(doctor_statement).first()

    if doctor is None:
        raise ValueError("Doctor not found")

    # 4. Определяем день недели.
    day_of_week = appointment_data.appointment_date.weekday()

    # 5. Получаем расписание врача на этот день.
    schedule_statement = select(DoctorSchedule).where(
        DoctorSchedule.doctor_id == doctor.id,
        DoctorSchedule.day_of_week == day_of_week,
    )

    schedules = list(db.scalars(schedule_statement).all())

    if not schedules:
        raise ValueError("Doctor does not work on this day")

    # 6. Проверяем, подходит ли выбранное время.
    matching_schedule = None
    appointment_end = None

    for schedule in schedules:

        if appointment_data.start_time < schedule.start_time:
            continue

        appointment_duration = timedelta(
            minutes=schedule.slot_duration
        )

        start_datetime = datetime.combine(
            appointment_data.appointment_date,
            appointment_data.start_time,
        )

        end_datetime = start_datetime + appointment_duration

        calculated_end = end_datetime.time()

        if calculated_end > schedule.end_time:
            continue

        # Проверяем соответствие времени началу слотов.
        start_minutes = (
            appointment_data.start_time.hour * 60
            + appointment_data.start_time.minute
        )

        schedule_minutes = (
            schedule.start_time.hour * 60
            + schedule.start_time.minute
        )

        difference = start_minutes - schedule_minutes

        if difference % schedule.slot_duration != 0:
            continue

        matching_schedule = schedule
        appointment_end = calculated_end
        break

    if matching_schedule is None:
        raise ValueError("Selected time is outside the doctor's available slots")

    # 7. Проверяем пересечение с существующими записями.
    conflict_statement = select(Appointment).where(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date == appointment_data.appointment_date,
        Appointment.status != AppointmentStatus.CANCELLED,
        Appointment.start_time < appointment_end,
        Appointment.end_time > appointment_data.start_time,
    )

    doctor_conflict = db.scalars(conflict_statement).first()

    if doctor_conflict:
        raise ValueError("This appointment slot is already booked")

    # 8. Проверяем, что пациент не записан на это же время.
    patient_conflict_statement = select(Appointment).where(
        Appointment.patient_id == patient.id,
        Appointment.appointment_date == appointment_data.appointment_date,
        Appointment.status != AppointmentStatus.CANCELLED,
        Appointment.start_time < appointment_end,
        Appointment.end_time > appointment_data.start_time,
    )

    patient_conflict = db.scalars(patient_conflict_statement).first()

    if patient_conflict:
        raise ValueError("You already have an appointment at this time")

    # 9. Создаём запись.
    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
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