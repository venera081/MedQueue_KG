from fastapi import FastAPI

app = FastAPI(
    title="MedQueue KG",
    description="API для записи пайиентов в клиники Кыргызстана",
    version="0.1.0",
)

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