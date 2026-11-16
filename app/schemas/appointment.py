from datetime import date, time, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import AppointmentStatus


class AppointmentCreate(BaseModel):
    doctor_id: int = Field(gt=0)
    appointment_date: date
    start_time: time


class AppointmentUpdate(BaseModel):
    appointment_date: date | None = None
    start_time: time | None = None

    @model_validator(mode="after")
    def validate_update_fields(self):
        if (
            self.appointment_date is None
            and self.start_time is None
        ):
            raise ValueError(
                "At least one field must be provided"
            )

        return self


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