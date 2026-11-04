from pydantic import BaseModel, ConfigDict


class SpecializationCreate(BaseModel):
    name: str
    description: str | None = None


class SpecializationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None