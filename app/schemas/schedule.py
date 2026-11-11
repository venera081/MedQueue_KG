from datetime import time

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ScheduleCreate(BaseModel):
    doctor_id: int = Field(gt=0)
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
    slot_duration: int = Field(default=30, gt=0)

    @model_validator(mode="after")
    def validate_schedule(self):
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be earlier than end time")

        return self


class ScheduleUpdate(BaseModel):
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
    slot_duration: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_schedule(self):
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be earlier than end time")

        return self


class ScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    doctor_id: int
    day_of_week: int
    start_time: time
    end_time: time
    slot_duration: int