from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.clinic import Clinic
from app.schemas.clinic import ClinicCreate


def create_clinic(db: Session, clinic_data: ClinicCreate) -> Clinic:
    clinic = Clinic(
        name=clinic_data.name,
        address=clinic_data.address,
        phone=clinic_data.phone,
    )
    db.add(clinic)
    db.commit()
    db.refresh(clinic)
    return clinic


def get_clinics(db: Session) -> list[Clinic]:
    statement = select(Clinic)
    return list(db.scalars(statement).all())


def get_clinic_by_id(db: Session, clinic_id: int) -> Clinic | None:
    statement = select(Clinic).where(Clinic.id == clinic_id)
    return db.scalars(statement).first()


def update_clinic(
    db: Session,
    clinic_id: int,
    clinic_data: ClinicCreate,
) -> Clinic | None:
    clinic = get_clinic_by_id(db, clinic_id)

    if clinic is None:
        return None

    clinic.name = clinic_data.name
    clinic.address = clinic_data.address
    clinic.phone = clinic_data.phone

    db.commit()
    db.refresh(clinic)

    return clinic


def delete_clinic(db: Session, clinic_id: int) -> bool:
    clinic = get_clinic_by_id(db, clinic_id)

    if clinic is None:
        return False

    db.delete(clinic)
    db.commit()

    return True