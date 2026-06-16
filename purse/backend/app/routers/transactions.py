from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import uuid

from app.database import get_db
from app.models.transaction import Transaction
from app.models.merchant_override import MerchantOverride
from app.config import settings

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


class CategoryUpdate(BaseModel):
    category: str
    save_as_merchant_rule: bool = True


@router.patch("/{transaction_id}/category")
async def update_transaction_category(
    transaction_id: uuid.UUID,
    update: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Manually override the category for a transaction.
    Optionally saves a merchant rule so future transactions from
    the same merchant are automatically categorised the same way.
    """
    result = await db.execute(
        select(Transaction).where(Transaction.id == transaction_id)
    )
    tx = result.scalar_one_or_none()

    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    tx.category_dashboard = update.category
    tx.category_source = "manual_override"
    tx.ml_confidence = None

    if update.save_as_merchant_rule and tx.merchant_clean:
        result = await db.execute(
            select(MerchantOverride).where(
                MerchantOverride.merchant_clean == tx.merchant_clean
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.category_dashboard = update.category
        else:
            db.add(MerchantOverride(
                merchant_clean=tx.merchant_clean,
                category_dashboard=update.category,
            ))

    await db.commit()
    await db.refresh(tx)

    return {
        "id": str(tx.id),
        "merchant_clean": tx.merchant_clean,
        "category_dashboard": tx.category_dashboard,
        "category_source": tx.category_source,
        "ml_confidence": float(tx.ml_confidence) if tx.ml_confidence else None,
    }


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