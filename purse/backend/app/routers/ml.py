from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.transaction import Transaction
from app.models.ml_training_log import MLTrainingLog
from app.services.ml import MLService

router = APIRouter(prefix="/api/v1/ml", tags=["ml"])


@router.post("/retrain")
async def retrain_model(request: Request, db: AsyncSession = Depends(get_db)):
    """Retrain the ML model on all approved categorised transactions."""
    ml_service = getattr(request.app.state, "ml_service", None)
    if ml_service is None:
        return {"success": False, "message": "ML service not initialised"}

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

    training_result = ml_service.train(corpus)

    if training_result.success:
        log_entry = MLTrainingLog(
            sample_count=training_result.sample_count,
            category_distribution=training_result.category_distribution,
            metrics={},
        )
        db.add(log_entry)
        await db.commit()

    return {
        "success": training_result.success,
        "message": training_result.message,
        "sample_count": training_result.sample_count,
        "category_distribution": training_result.category_distribution,
    }


@router.get("/training-log")
async def get_training_log(db: AsyncSession = Depends(get_db)):
    """Return history of ML training runs."""
    result = await db.execute(
        select(MLTrainingLog).order_by(MLTrainingLog.trained_at.desc())
    )
    logs = result.scalars().all()
    return [
        {
            "id": str(log.id),
            "trained_at": log.trained_at.isoformat(),
            "sample_count": log.sample_count,
            "category_distribution": log.category_distribution,
            "metrics": log.metrics,
        }
        for log in logs
    ]


@router.get("/predict-test")
async def predict_test(request: Request, merchant: str):
    """Temporary debug endpoint — remove before production."""
    ml_service = getattr(request.app.state, "ml_service", None)
    if ml_service is None:
        return {"error": "ML service not initialised"}
    prediction = ml_service.predict(merchant)
    return {
        "merchant": merchant,
        "category": prediction.category,
        "confidence": prediction.confidence,
        "source": prediction.source,
    }