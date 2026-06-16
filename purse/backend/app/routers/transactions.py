from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.transaction import Transaction
from app.config import settings

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


@router.get("/low-confidence")
async def get_low_confidence_transactions(
    db: AsyncSession = Depends(get_db),
):
    """
    Return ML-categorised transactions below the confidence threshold.
    These are surfaced for manual review — the active learning queue.
    """
    result = await db.execute(
        select(Transaction).where(
            Transaction.category_source == "ml",
            Transaction.ml_confidence < settings.ml_low_confidence_threshold,
        ).order_by(Transaction.ml_confidence.asc())
    )
    transactions = result.scalars().all()
    return [
        {
            "id": str(tx.id),
            "date": tx.date.isoformat(),
            "amount": float(tx.amount),
            "merchant_clean": tx.merchant_clean,
            "category_dashboard": tx.category_dashboard,
            "ml_confidence": float(tx.ml_confidence) if tx.ml_confidence else None,
        }
        for tx in transactions
    ]