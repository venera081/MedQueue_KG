from datetime import date, time, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AppointmentStatus


class AppointmentCreate(BaseModel):
    doctor_id: int = Field(gt=0)
    appointment_date: date
    start_time: time


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: date
    start_time: time
    end_time: time
    status: AppointmentStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus