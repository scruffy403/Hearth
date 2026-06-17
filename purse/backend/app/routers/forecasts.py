from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from datetime import date
import uuid

from app.database import get_db
from app.models.transaction import Transaction
from app.models.forecast_scenario import ForecastScenario


router = APIRouter(prefix="/api/v1/forecasts", tags=["forecasts"])


class ScenarioCreate(BaseModel):
    name: str
    days_ahead: int = 30
    exclude_categories: Optional[list[str]] = None
    exclude_tx_ids: Optional[list[uuid.UUID]] = None
    parameters: Optional[dict] = None


def scenario_to_dict(scenario: ForecastScenario) -> dict:
    return {
        "id": str(scenario.id),
        "name": scenario.name,
        "created_at": scenario.created_at.isoformat(),
        "days_ahead": scenario.days_ahead,
        "exclude_categories": scenario.exclude_categories or [],
        "exclude_tx_ids": [str(t) for t in (scenario.exclude_tx_ids or [])],
        "parameters": scenario.parameters or {},
    }


@router.get("/cashflow")
async def get_cashflow(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Return daily net cashflow (income minus expenses) for a date range.
    Used as the historical basis for forecasting charts.
    """
    filters = []
    if from_date:
        filters.append(Transaction.date >= from_date)
    if to_date:
        filters.append(Transaction.date <= to_date)

    stmt = (
        select(
            Transaction.date,
            func.sum(Transaction.amount).label("net"),
        )
        .where(*filters)
        .group_by(Transaction.date)
        .order_by(Transaction.date)
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        {"date": row.date.isoformat(), "net": float(row.net)}
        for row in rows
    ]


@router.post("/scenarios", status_code=201)
async def create_scenario(
    scenario: ScenarioCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new forecast scenario."""
    new_scenario = ForecastScenario(
        name=scenario.name,
        days_ahead=scenario.days_ahead,
        exclude_categories=scenario.exclude_categories,
        exclude_tx_ids=scenario.exclude_tx_ids,
        parameters=scenario.parameters,
    )
    db.add(new_scenario)
    await db.commit()
    await db.refresh(new_scenario)
    return scenario_to_dict(new_scenario)


@router.get("/scenarios")
async def list_scenarios(db: AsyncSession = Depends(get_db)):
    """List all saved forecast scenarios."""
    result = await db.execute(
        select(ForecastScenario).order_by(ForecastScenario.created_at.desc())
    )
    scenarios = result.scalars().all()
    return [scenario_to_dict(s) for s in scenarios]


@router.get("/scenarios/{scenario_id}")
async def get_scenario(
    scenario_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single forecast scenario by ID."""
    result = await db.execute(
        select(ForecastScenario).where(ForecastScenario.id == scenario_id)
    )
    scenario = result.scalar_one_or_none()
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario_to_dict(scenario)


@router.delete("/scenarios/{scenario_id}", status_code=204)
async def delete_scenario(
    scenario_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a forecast scenario."""
    result = await db.execute(
        select(ForecastScenario).where(ForecastScenario.id == scenario_id)
    )
    scenario = result.scalar_one_or_none()
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    await db.delete(scenario)
    await db.commit()