from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True,)
    clinic_id: Mapped[int] = mapped_column(ForeignKey("clinics.id"),)

    specialization_id: Mapped[int] = mapped_column(ForeignKey("specializations.id"),)

    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="doctor_profile")
    clinic = relationship("Clinic")
    specialization = relationship("Specialization", back_populates="doctors",)
    schedules = relationship("DoctorSchedule", back_populates="doctor", cascade="all, delete-orphan",)

class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True,)

    date_of_birth: Mapped[str | None] = mapped_column(String(10), nullable=True,)
    user = relationship("User", back_populates="patient_profile")