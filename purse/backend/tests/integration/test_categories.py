import pytest
import uuid
from datetime import date
from decimal import Decimal


async def test_get_categories_returns_dashboard_list(client, db_session):
    response = await client.get("/api/v1/categories")
    assert response.status_code == 200
    data = response.json()
    assert "Groceries" in data
    assert "Other" in data


async def test_categories_summary_returns_totals_per_category(client, db_session):
    from app.models.transaction import Transaction

    transactions = [
        ("Groceries", Decimal("-50.00")),
        ("Groceries", Decimal("-30.00")),
        ("Eating Out", Decimal("-20.00")),
    ]
    for category, amount in transactions:
        tx = Transaction(
            ynab_transaction_id=f"test-{uuid.uuid4()}",
            date=date(2024, 1, 15),
            amount=amount,
            merchant_raw="Test",
            merchant_clean="Test",
            category_ynab=category,
            category_dashboard=category,
            category_source="ynab",
            ynab_approved=True,
            is_transfer=False,
        )
        db_session.add(tx)
    await db_session.flush()

    response = await client.get(
        "/api/v1/categories/summary",
        params={"from_date": "2024-01-01", "to_date": "2024-02-01"}
    )
    assert response.status_code == 200
    data = response.json()

    groceries = next(c for c in data if c["category"] == "Groceries")
    assert groceries["total"] == 80.00
    assert groceries["transaction_count"] == 2

    eating_out = next(c for c in data if c["category"] == "Eating Out")
    assert eating_out["total"] == 20.00


async def test_categories_trends_returns_monthly_breakdown(client, db_session):
    from app.models.transaction import Transaction

    transactions = [
        (date(2024, 1, 10), Decimal("-50.00")),
        (date(2024, 2, 10), Decimal("-30.00")),
    ]
    for tx_date, amount in transactions:
        tx = Transaction(
            ynab_transaction_id=f"test-{uuid.uuid4()}",
            date=tx_date,
            amount=amount,
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

    response = await client.get(
        "/api/v1/categories/trends",
        params={"category": "Groceries", "months": 6}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all("month" in d and "total" in d for d in data)


async def test_categories_merchants_returns_top_merchants(client, db_session):
    from app.models.transaction import Transaction

    transactions = [
        (date(2024, 1, 15), "Tesco", Decimal("-50.00")),
        (date(2024, 1, 15), "Tesco", Decimal("-30.00")),
        (date(2024, 1, 15), "Sainsbury's", Decimal("-20.00")),
        (date(2020, 1, 15), "Old Merchant", Decimal("-999.00")),  # out of range
    ]
    for tx_date, merchant, amount in transactions:
        tx = Transaction(
            ynab_transaction_id=f"test-{uuid.uuid4()}",
            date=tx_date,
            amount=amount,
            merchant_raw=merchant,
            merchant_clean=merchant,
            category_ynab="Groceries",
            category_dashboard="Groceries",
            category_source="ynab",
            ynab_approved=True,
            is_transfer=False,
        )
        db_session.add(tx)
    await db_session.flush()

    response = await client.get(
        "/api/v1/categories/merchants",
        params={
            "category": "Groceries",
            "from_date": "2024-01-01",
            "to_date": "2024-02-01",
        },
    )
    assert response.status_code == 200
    data = response.json()

    merchant_names = [m["merchant"] for m in data]
    assert "Old Merchant" not in merchant_names

    tesco = next(m for m in data if m["merchant"] == "Tesco")
    assert tesco["total"] == 80.00
    assert tesco["transaction_count"] == 2