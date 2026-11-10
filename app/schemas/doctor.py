from pydantic import BaseModel, ConfigDict

from app.schemas.clinic import ClinicResponse
from app.schemas.specialization import SpecializationResponse


class DoctorCreate(BaseModel):
    user_id: int
    clinic_id: int
    specialization_id: int
    experience_years: int = 0
    description: str | None = None


class DoctorUpdate(BaseModel):
    clinic_id: int
    specialization_id: int
    experience_years: int
    description: str | None = None


class DoctorUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str
    last_name: str
    phone: str


class DoctorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    clinic_id: int
    specialization_id: int
    experience_years: int
    description: str | None

    user: DoctorUserResponse
    clinic: ClinicResponse
    specialization: SpecializationResponse