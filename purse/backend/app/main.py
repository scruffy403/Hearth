from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.transaction import Transaction
from app.routers import sync, ml as ml_router, transactions, categories
from app.services.ml import MLService
from sync.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Train ML model on startup
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Transaction).where(
                Transaction.ynab_approved == True,
                Transaction.category_dashboard != "Other",
                Transaction.category_source != "ml",
                Transaction.merchant_clean != None,
            )
        )
        transactions = result.scalars().all()
        corpus = [
            {
                "merchant_clean": tx.merchant_clean,
                "category": tx.category_dashboard,
            }
            for tx in transactions
            if tx.merchant_clean
        ]
        ml_service = MLService(min_samples=5)
        if corpus:
            training_result = ml_service.train(corpus)
            print(f"ML model trained on startup: {training_result.message}")
            print(f"ML service instance id: {id(ml_service)}")

    # Store on app state so all request handlers can access the same instance
    app.state.ml_service = ml_service

    start_scheduler(app=app)
    yield
    stop_scheduler()


app = FastAPI(
    title="Hearth Purse",
    description="Household finance dashboard API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(sync.router)
app.include_router(ml_router.router)
app.include_router(transactions.router)
app.include_router(categories.router)


@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "env": settings.app_env,
    }