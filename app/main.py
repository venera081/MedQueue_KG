from fastapi import FastAPI

from app.db.base import Base
from app.db.session import engine

from app.api.v1.clinics import router as clinics_router
from app.api.v1.auth import router as auth_router
from app.api.v1.specializations import router as specializations_router

from app.models.clinic import Clinic
from app.models.user import User
from app.models.profile import DoctorProfile, PatientProfile
from app.models.specialization import Specialization
from app.models.schedule import DoctorSchedule


app = FastAPI(
    title="MedQueue KG",
    description="API для записи пациентов в клиники Кыргызстана",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)

app.include_router(clinics_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(specializations_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Welcome to MedQueue KG!",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
    }