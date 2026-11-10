from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.profile import DoctorProfile
from app.models.user import User
from app.models.clinic import Clinic
from app.models.specialization import Specialization
from app.models.enums import UserRole

from app.schemas.doctor import DoctorCreate, DoctorUpdate


def get_doctor_by_id(
    db: Session,
    doctor_id: int,
) -> DoctorProfile | None:
    statement = (
        select(DoctorProfile)
        .options(
            selectinload(DoctorProfile.user),
            selectinload(DoctorProfile.clinic),
            selectinload(DoctorProfile.specialization),
        )
        .where(DoctorProfile.id == doctor_id)
    )

    return db.scalars(statement).first()


def get_doctors(db: Session) -> list[DoctorProfile]:
    statement = (
        select(DoctorProfile)
        .options(
            selectinload(DoctorProfile.user),
            selectinload(DoctorProfile.clinic),
            selectinload(DoctorProfile.specialization),
        )
    )

    return list(db.scalars(statement).all())


def create_doctor(
    db: Session,
    doctor_data: DoctorCreate,
) -> tuple[DoctorProfile | None, str | None]:

    user = db.get(User, doctor_data.user_id)

    if user is None:
        return None, "user_not_found"

    if user.role != UserRole.DOCTOR:
        return None, "user_not_doctor"

    if not user.is_active:
        return None, "user_inactive"

    if user.doctor_profile is not None:
        return None, "profile_exists"

    clinic = db.get(Clinic, doctor_data.clinic_id)

    if clinic is None:
        return None, "clinic_not_found"

    specialization = db.get(
        Specialization,
        doctor_data.specialization_id,
    )

    if specialization is None:
        return None, "specialization_not_found"

    doctor = DoctorProfile(
        user_id=doctor_data.user_id,
        clinic_id=doctor_data.clinic_id,
        specialization_id=doctor_data.specialization_id,
        experience_years=doctor_data.experience_years,
        description=doctor_data.description,
    )

    db.add(doctor)
    db.commit()

    return get_doctor_by_id(db, doctor.id), None


def update_doctor(
    db: Session,
    doctor_id: int,
    doctor_data: DoctorUpdate,
) -> tuple[DoctorProfile | None, str | None]:

    doctor = get_doctor_by_id(db, doctor_id)

    if doctor is None:
        return None, "doctor_not_found"

    clinic = db.get(Clinic, doctor_data.clinic_id)

    if clinic is None:
        return None, "clinic_not_found"

    specialization = db.get(
        Specialization,
        doctor_data.specialization_id,
    )

    if specialization is None:
        return None, "specialization_not_found"

    doctor.clinic_id = doctor_data.clinic_id
    doctor.specialization_id = doctor_data.specialization_id
    doctor.experience_years = doctor_data.experience_years
    doctor.description = doctor_data.description

    db.commit()

    return get_doctor_by_id(db, doctor_id), None


def delete_doctor(db: Session, doctor_id: int) -> bool:
    doctor = get_doctor_by_id(db, doctor_id)

    if doctor is None:
        return False

    db.delete(doctor)
    db.commit()

    return True