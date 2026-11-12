from datetime import date, time, datetime, timezone

from sqlalchemy import (
    Date,
    Time,
    DateTime,
    ForeignKey,
    Enum as SQLAlchemyEnum,
    Index,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import AppointmentStatus


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patient_profiles.id"),
        nullable=False,
    )

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctor_profiles.id"),
        nullable=False,
    )

    appointment_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    status: Mapped[AppointmentStatus] = mapped_column(
        SQLAlchemyEnum(AppointmentStatus),
        default=AppointmentStatus.BOOKED,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


# Один врач не может иметь две активные записи на одно время.
Index(
    "uq_doctor_appointment_slot",
    Appointment.doctor_id,
    Appointment.appointment_date,
    Appointment.start_time,
    unique=True,
    sqlite_where=text("status != 'CANCELLED'"),
)

# Один пациент не может записаться к разным врачам на одно время.
Index(
    "uq_patient_appointment_slot",
    Appointment.patient_id,
    Appointment.appointment_date,
    Appointment.start_time,
    unique=True,
    sqlite_where=text("status != 'CANCELLED'"),
)