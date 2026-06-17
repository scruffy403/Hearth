from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from decimal import Decimal
from datetime import date

from app.database import get_db
from app.models.budget_config import BudgetConfig
from app.models.transaction import Transaction


router = APIRouter(prefix="/api/v1/budgets", tags=["budgets"])


class BudgetUpdate(BaseModel):
    mode: str = "manual"
    monthly_amount: Optional[float] = None


def budget_to_dict(budget: BudgetConfig) -> dict:
    return {
        "category_dashboard": budget.category_dashboard,
        "mode": budget.mode,
        "monthly_amount": float(budget.monthly_amount) if budget.monthly_amount else None,
    }


@router.get("")
async def list_budgets(db: AsyncSession = Depends(get_db)):
    """Return all budget configurations."""
    result = await db.execute(select(BudgetConfig))
    budgets = result.scalars().all()
    return [budget_to_dict(b) for b in budgets]


@router.get("/vs-actual")
async def budgets_vs_actual(db: AsyncSession = Depends(get_db)):
    """
    Compare budgeted amounts against actual spend for the current month.
    Only categories with a budget configured are included.
    """
    budget_result = await db.execute(select(BudgetConfig))
    budgets = budget_result.scalars().all()

    today = date.today()
    month_start = date(today.year, today.month, 1)

    comparisons = []
    for budget in budgets:
        actual_result = await db.execute(
            select(func.sum(Transaction.amount)).where(
                Transaction.category_dashboard == budget.category_dashboard,
                Transaction.date >= month_start,
                Transaction.date <= today,
                Transaction.amount < 0,
            )
        )
        actual_total = actual_result.scalar() or Decimal("0")
        actual = abs(float(actual_total))
        budgeted = float(budget.monthly_amount) if budget.monthly_amount else 0.0

        comparisons.append({
            "category": budget.category_dashboard,
            "budgeted": budgeted,
            "actual": actual,
            "remaining": round(budgeted - actual, 2),
        })

    return comparisons


@router.put("/{category}")
async def upsert_budget(
    category: str,
    update: BudgetUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create or update the budget configuration for a category.
    """
    result = await db.execute(
        select(BudgetConfig).where(BudgetConfig.category_dashboard == category)
    )
    budget = result.scalar_one_or_none()

    monthly_amount = (
        Decimal(str(update.monthly_amount))
        if update.monthly_amount is not None
        else None
    )

    if budget:
        budget.mode = update.mode
        budget.monthly_amount = monthly_amount
    else:
        budget = BudgetConfig(
            category_dashboard=category,
            mode=update.mode,
            monthly_amount=monthly_amount,
        )
        db.add(budget)

    await db.commit()
    await db.refresh(budget)
    return budget_to_dict(budget)