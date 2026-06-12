from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.routers import sync


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Hearth Purse",
    description="Household finance dashboard API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(sync.router)


@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "env": settings.app_env,
    }