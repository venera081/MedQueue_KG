from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.enums import UserRole


def create_user(
        db: Session,
        email: str,
        hashed_password: str,
        first_name: str,
        last_name: str,
        phone: str,
        role: UserRole = UserRole.PATIENT,
) -> User:

    user = User(
        email=email,
        hashed_password=hashed_password,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        role=role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user_by_id(db: Session, user_id: int) -> User | None:
    statement = select(User).where(User.id == user_id)
    return db.scalars(statement).first()

def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return db.scalars(statement).first()

def get_users(db: Session) -> list[User]:
    statement = select(User)
    return list(db.scalars(statement).all())


def update_user(
    db: Session,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    phone: str | None = None,
) -> User | None:

    user = get_user_by_id(db, user_id)

    if user is None:
        return None

    if first_name is not None:
        user.first_name = first_name

    if last_name is not None:
        user.last_name = last_name

    if phone is not None:
        user.phone = phone

    db.commit()
    db.refresh(user)

    return user


def deactivate_user(db: Session, user_id: int) -> User | None:
    user = get_user_by_id(db, user_id)

    if user is None:
        return None

    user.is_active = False

    db.commit()
    db.refresh(user)

    return user