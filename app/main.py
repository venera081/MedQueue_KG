from fastapi import FastAPI

from app.db.base import Base
from app.db.session import engine
from app.api.v1.clinics import router as clinics_router

app = FastAPI(
    title="MedQueue KG",
    description="API для записи пациентов в клиники Кыргызстана",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)

app.include_router(clinics_router, prefix="/api/v1")


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