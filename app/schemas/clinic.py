from pydantic import BaseModel, ConfigDict


class ClinicCreate(BaseModel):
    name: str
    address: str
    phone: str


class ClinicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    phone: str