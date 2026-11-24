from pydantic import BaseModel, ConfigDict

from app.schemas.clinic import ClinicResponse
from app.schemas.specialization import SpecializationResponse
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class DoctorAccountCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    phone: str

    clinic_id: int
    specialization_id: int
    experience_years: int = Field(default=0, ge=0)
    description: str | None = None

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