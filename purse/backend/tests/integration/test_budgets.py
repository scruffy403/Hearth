import pytest
from decimal import Decimal
from datetime import date
import uuid


async def test_get_budgets_returns_empty_list_initially(client, db_session):
    response = await client.get("/api/v1/budgets")
    assert response.status_code == 200
    assert response.json() == []


async def test_put_budget_creates_new_config(client, db_session):
    response = await client.put(
        "/api/v1/budgets/Groceries",
        json={"mode": "manual", "monthly_amount": 400.00}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category_dashboard"] == "Groceries"
    assert data["mode"] == "manual"
    assert data["monthly_amount"] == 400.00


async def test_put_budget_updates_existing_config(client, db_session):
    from app.models.budget_config import BudgetConfig

    existing = BudgetConfig(
        category_dashboard="Groceries",
        mode="manual",
        monthly_amount=Decimal("300.00"),
    )
    db_session.add(existing)
    await db_session.flush()

    response = await client.put(
        "/api/v1/budgets/Groceries",
        json={"mode": "manual", "monthly_amount": 450.00}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["monthly_amount"] == 450.00


async def test_get_budgets_lists_all_configs(client, db_session):
    from app.models.budget_config import BudgetConfig

    db_session.add(BudgetConfig(category_dashboard="Groceries", mode="manual", monthly_amount=Decimal("400.00")))
    db_session.add(BudgetConfig(category_dashboard="Eating Out", mode="manual", monthly_amount=Decimal("150.00")))
    await db_session.flush()

    response = await client.get("/api/v1/budgets")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


async def test_budgets_vs_actual_compares_current_month_spend(client, db_session):
    from app.models.budget_config import BudgetConfig
    from app.models.transaction import Transaction

    db_session.add(BudgetConfig(category_dashboard="Groceries", mode="manual", monthly_amount=Decimal("400.00")))

    today = date.today()
    tx = Transaction(
        ynab_transaction_id=f"test-{uuid.uuid4()}",
        date=date(today.year, today.month, 1),
        amount=Decimal("-150.00"),
        merchant_raw="Tesco",
        merchant_clean="Tesco",
        category_ynab="Groceries",
        category_dashboard="Groceries",
        category_source="ynab",
        ynab_approved=True,
        is_transfer=False,
    )
    db_session.add(tx)
    await db_session.flush()

    response = await client.get("/api/v1/budgets/vs-actual")
    assert response.status_code == 200
    data = response.json()

    groceries = next(c for c in data if c["category"] == "Groceries")
    assert groceries["budgeted"] == 400.00
    assert groceries["actual"] == 150.00
    assert groceries["remaining"] == 250.00