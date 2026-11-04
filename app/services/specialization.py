from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.specialization import Specialization
from app.models.profile import DoctorProfile
from app.schemas.specialization import SpecializationCreate


def create_specialization(
    db: Session,
    specialization_data: SpecializationCreate,
) -> Specialization:
    specialization = Specialization(
        name=specialization_data.name,
        description=specialization_data.description,
    )

    db.add(specialization)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError(
            "Specialization with this name already exists."
        ) from exc

    db.refresh(specialization)
    return specialization


def get_specializations(db: Session) -> list[Specialization]:
    statement = select(Specialization)
    return list(db.scalars(statement).all())


def get_specialization_by_id(
    db: Session,
    specialization_id: int,
) -> Specialization | None:
    statement = select(Specialization).where(
        Specialization.id == specialization_id
    )
    return db.scalars(statement).first()


def update_specialization(
    db: Session,
    specialization_id: int,
    specialization_data: SpecializationCreate,
) -> Specialization | None:
    specialization = get_specialization_by_id(db, specialization_id)

    if specialization is None:
        return None

    specialization.name = specialization_data.name
    specialization.description = specialization_data.description

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError(
            "Specialization with this name already exists."
        ) from exc

    db.refresh(specialization)
    return specialization


def delete_specialization(
    db: Session,
    specialization_id: int,
) -> bool | None:
    specialization = get_specialization_by_id(db, specialization_id)

    if specialization is None:
        return None

    doctor_statement = select(DoctorProfile).where(
        DoctorProfile.specialization_id == specialization_id
    )
    doctors = db.scalars(doctor_statement).first()

    if doctors is not None:
        return False

    db.delete(specialization)
    db.commit()

    return True