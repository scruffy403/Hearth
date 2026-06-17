from collections import defaultdict
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import date

from app.database import get_db
from app.models.transaction import Transaction


router = APIRouter(prefix="/api/v1/anomalies", tags=["anomalies"])


def calculate_iqr_bounds(amounts: list[float]) -> tuple[float, float]:
    """
    Calculate IQR-based outlier bounds for a list of amounts.
    Returns (lower_bound, upper_bound). Values outside these bounds
    are considered anomalous.

    Standard IQR method: bounds are Q1 - 1.5*IQR and Q3 + 1.5*IQR.
    Requires at least 4 data points to compute meaningfully.
    """
    if len(amounts) < 4:
        return (float("-inf"), float("inf"))

    sorted_amounts = sorted(amounts)
    n = len(sorted_amounts)

    def percentile(data: list[float], pct: float) -> float:
        k = (len(data) - 1) * pct
        f = int(k)
        c = f + 1 if f + 1 < len(data) else f
        if f == c:
            return data[f]
        return data[f] + (data[c] - data[f]) * (k - f)

    q1 = percentile(sorted_amounts, 0.25)
    q3 = percentile(sorted_amounts, 0.75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    return (lower_bound, upper_bound)


@router.get("")
async def get_anomalies(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Flag transactions that are unusual relative to typical spending
    in their category, using IQR-based outlier detection.

    Compares the magnitude of each expense against the distribution
    of expenses in the same category. Income and transfers are excluded.
    """
    filters = [Transaction.amount < 0]
    if from_date:
        filters.append(Transaction.date >= from_date)
    if to_date:
        filters.append(Transaction.date <= to_date)

    result = await db.execute(
        select(Transaction).where(*filters)
    )
    transactions = result.scalars().all()

    # Group by category to compute per-category bounds
    by_category: dict[str, list[Transaction]] = defaultdict(list)
    for tx in transactions:
        by_category[tx.category_dashboard].append(tx)

    anomalies = []
    for category, txs in by_category.items():
        amounts = [abs(float(tx.amount)) for tx in txs]
        lower, upper = calculate_iqr_bounds(amounts)

        for tx in txs:
            magnitude = abs(float(tx.amount))
            if magnitude > upper:
                anomalies.append({
                    "id": str(tx.id),
                    "date": tx.date.isoformat(),
                    "amount": float(tx.amount),
                    "merchant_clean": tx.merchant_clean,
                    "category_dashboard": tx.category_dashboard,
                    "category_upper_bound": round(upper, 2),
                })

    anomalies.sort(key=lambda a: a["date"], reverse=True)
    return anomalies