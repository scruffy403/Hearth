import pytest
import uuid
from datetime import date
from decimal import Decimal


async def test_cashflow_returns_daily_net_totals(client, db_session):
    from app.models.transaction import Transaction

    transactions = [
        (date(2024, 1, 10), Decimal("-50.00")),
        (date(2024, 1, 10), Decimal("-20.00")),
        (date(2024, 1, 11), Decimal("2000.00")),
    ]
    for tx_date, amount in transactions:
        tx = Transaction(
            ynab_transaction_id=f"test-{uuid.uuid4()}",
            date=tx_date,
            amount=amount,
            merchant_raw="Test",
            merchant_clean="Test",
            category_ynab="Groceries",
            category_dashboard="Groceries" if amount < 0 else "Income",
            category_source="ynab",
            ynab_approved=True,
            is_transfer=False,
        )
        db_session.add(tx)
    await db_session.flush()

    response = await client.get(
        "/api/v1/forecasts/cashflow",
        params={"from_date": "2024-01-01", "to_date": "2024-02-01"}
    )
    assert response.status_code == 200
    data = response.json()

    day1 = next(d for d in data if d["date"] == "2024-01-10")
    assert day1["net"] == -70.00

    day2 = next(d for d in data if d["date"] == "2024-01-11")
    assert day2["net"] == 2000.00


async def test_create_scenario(client, db_session):
    response = await client.post(
        "/api/v1/forecasts/scenarios",
        json={
            "name": "Skip holiday spending",
            "days_ahead": 30,
            "exclude_categories": ["Holidays"],
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Skip holiday spending"
    assert data["days_ahead"] == 30
    assert "Holidays" in data["exclude_categories"]
    assert "id" in data


async def test_list_scenarios(client, db_session):
    await client.post(
        "/api/v1/forecasts/scenarios",
        json={"name": "Scenario A", "days_ahead": 30}
    )
    await client.post(
        "/api/v1/forecasts/scenarios",
        json={"name": "Scenario B", "days_ahead": 60}
    )

    response = await client.get("/api/v1/forecasts/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


async def test_get_single_scenario(client, db_session):
    create_response = await client.post(
        "/api/v1/forecasts/scenarios",
        json={"name": "Test Scenario", "days_ahead": 30}
    )
    scenario_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/forecasts/scenarios/{scenario_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Scenario"


async def test_delete_scenario(client, db_session):
    create_response = await client.post(
        "/api/v1/forecasts/scenarios",
        json={"name": "To Delete", "days_ahead": 30}
    )
    scenario_id = create_response.json()["id"]

    delete_response = await client.delete(f"/api/v1/forecasts/scenarios/{scenario_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/api/v1/forecasts/scenarios/{scenario_id}")
    assert get_response.status_code == 404


async def test_get_nonexistent_scenario_returns_404(client, db_session):
    response = await client.get(f"/api/v1/forecasts/scenarios/{uuid.uuid4()}")
    assert response.status_code == 404