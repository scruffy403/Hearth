from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import date

from app.database import get_db
from app.models.transaction import Transaction
from app.services.category_mapping import get_dashboard_categories


router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@router.get("")
async def list_categories():
    """Return all dashboard category names in display order."""
    return get_dashboard_categories()


@router.get("/summary")
async def categories_summary(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Return total spend and transaction count per category for a date range.
    Only includes expenses (negative amounts) — income is excluded.
    """
    filters = [Transaction.amount < 0]
    if from_date:
        filters.append(Transaction.date >= from_date)
    if to_date:
        filters.append(Transaction.date <= to_date)

    stmt = (
        select(
            Transaction.category_dashboard,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("transaction_count"),
        )
        .where(and_(*filters))
        .group_by(Transaction.category_dashboard)
        .order_by(func.sum(Transaction.amount))
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "category": row.category_dashboard,
            "total": abs(float(row.total)),
            "transaction_count": row.transaction_count,
        }
        for row in rows
    ]


@router.get("/trends")
async def categories_trends(
    category: str = Query(...),
    months: int = Query(12, le=60),
    db: AsyncSession = Depends(get_db),
):
    """
    Return monthly spend totals for a single category over the
    last N months. Used for trend charts.
    """
    month_label = func.to_char(Transaction.date, "YYYY-MM").label("month")

    stmt = (
        select(
            month_label,
            func.sum(Transaction.amount).label("total"),
        )
        .where(
            Transaction.category_dashboard == category,
            Transaction.amount < 0,
        )
        .group_by(month_label)
        .order_by(month_label.desc())
        .limit(months)
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        {"month": row.month, "total": abs(float(row.total))}
        for row in reversed(rows)
    ]


@router.get("/merchants")
async def categories_merchants(
    category: str = Query(...),
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Return top merchants by total spend within a category.
    Used to answer 'where is my Groceries money actually going'.
    """
    stmt = (
        select(
            Transaction.merchant_clean,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("transaction_count"),
        )
        .where(
            Transaction.category_dashboard == category,
            Transaction.amount < 0,
        )
        .group_by(Transaction.merchant_clean)
        .order_by(func.sum(Transaction.amount))
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "merchant": row.merchant_clean,
            "total": abs(float(row.total)),
            "transaction_count": row.transaction_count,
        }
        for row in rows
    ]