from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.routers import sync
from sync.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()


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