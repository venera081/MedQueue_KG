from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile import DoctorProfile
from app.models.schedule import DoctorSchedule

from app.schemas.schedule import ScheduleCreate, ScheduleUpdate


def get_schedule_by_id(
    db: Session,
    schedule_id: int,
) -> DoctorSchedule | None:
    return db.get(DoctorSchedule, schedule_id)


def get_schedules(db: Session) -> list[DoctorSchedule]:
    statement = select(DoctorSchedule)

    return list(db.scalars(statement).all())


def has_schedule_conflict(
    db: Session,
    doctor_id: int,
    day_of_week: int,
    start_time,
    end_time,
    exclude_schedule_id: int | None = None,
) -> bool:
    statement = select(DoctorSchedule).where(
        DoctorSchedule.doctor_id == doctor_id,
        DoctorSchedule.day_of_week == day_of_week,
        DoctorSchedule.start_time < end_time,
        DoctorSchedule.end_time > start_time,
    )

    if exclude_schedule_id is not None:
        statement = statement.where(
            DoctorSchedule.id != exclude_schedule_id
        )

    return db.scalars(statement).first() is not None


def create_schedule(
    db: Session,
    schedule_data: ScheduleCreate,
) -> tuple[DoctorSchedule | None, str | None]:

    doctor = db.get(DoctorProfile, schedule_data.doctor_id)

    if doctor is None:
        return None, "doctor_not_found"

    conflict = has_schedule_conflict(
        db=db,
        doctor_id=schedule_data.doctor_id,
        day_of_week=schedule_data.day_of_week,
        start_time=schedule_data.start_time,
        end_time=schedule_data.end_time,
    )

    if conflict:
        return None, "schedule_conflict"

    schedule = DoctorSchedule(
        doctor_id=schedule_data.doctor_id,
        day_of_week=schedule_data.day_of_week,
        start_time=schedule_data.start_time,
        end_time=schedule_data.end_time,
        slot_duration=schedule_data.slot_duration,
    )

    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    return schedule, None


def update_schedule(
    db: Session,
    schedule_id: int,
    schedule_data: ScheduleUpdate,
) -> tuple[DoctorSchedule | None, str | None]:

    schedule = get_schedule_by_id(db, schedule_id)

    if schedule is None:
        return None, "schedule_not_found"

    conflict = has_schedule_conflict(
        db=db,
        doctor_id=schedule.doctor_id,
        day_of_week=schedule_data.day_of_week,
        start_time=schedule_data.start_time,
        end_time=schedule_data.end_time,
        exclude_schedule_id=schedule_id,
    )

    if conflict:
        return None, "schedule_conflict"

    schedule.day_of_week = schedule_data.day_of_week
    schedule.start_time = schedule_data.start_time
    schedule.end_time = schedule_data.end_time
    schedule.slot_duration = schedule_data.slot_duration

    db.commit()
    db.refresh(schedule)

    return schedule, None


def delete_schedule(
    db: Session,
    schedule_id: int,
) -> bool:

    schedule = get_schedule_by_id(db, schedule_id)

    if schedule is None:
        return False

    db.delete(schedule)
    db.commit()

    return True