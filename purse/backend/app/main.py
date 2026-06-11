from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Scheduler will be started here in Phase 2
    yield
    # Shutdown
    # Scheduler will be stopped here in Phase 2

app = FastAPI(
    title="Hearth Purse",
    description="Household finance dashboard API",
    version="0.1.0",
    lifespan=lifespan,
)

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "env": settings.app_env,
    }