from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.schedule import (
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse,
)

from app.services.schedule import (
    create_schedule,
    get_schedules,
    get_schedule_by_id,
    update_schedule,
    delete_schedule,
)


router = APIRouter(
    prefix="/schedules",
    tags=["Schedules"],
)


@router.post(
    "/",
    response_model=ScheduleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_schedule_endpoint(
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db),
):
    schedule, error = create_schedule(db, schedule_data)

    if error == "doctor_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    if error == "schedule_conflict":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Schedule overlaps with an existing schedule",
        )

    return schedule


@router.get(
    "/",
    response_model=list[ScheduleResponse],
)
def get_schedules_endpoint(
    db: Session = Depends(get_db),
):
    return get_schedules(db)


@router.get(
    "/{schedule_id}",
    response_model=ScheduleResponse,
)
def get_schedule_endpoint(
    schedule_id: int,
    db: Session = Depends(get_db),
):
    schedule = get_schedule_by_id(db, schedule_id)

    if schedule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    return schedule


@router.put(
    "/{schedule_id}",
    response_model=ScheduleResponse,
)
def update_schedule_endpoint(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    db: Session = Depends(get_db),
):
    schedule, error = update_schedule(
        db,
        schedule_id,
        schedule_data,
    )

    if error == "schedule_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    if error == "schedule_conflict":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Schedule overlaps with an existing schedule",
        )

    return schedule


@router.delete(
    "/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_schedule_endpoint(
    schedule_id: int,
    db: Session = Depends(get_db),
):
    deleted = delete_schedule(db, schedule_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )