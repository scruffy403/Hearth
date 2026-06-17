import pytest
from unittest.mock import patch
import uuid


async def test_patch_transaction_category_updates_dashboard(client, db_session):
    from app.models.transaction import Transaction
    from datetime import date
    from decimal import Decimal

    tx = Transaction(
        ynab_transaction_id=f"test-{uuid.uuid4()}",
        date=date(2024, 1, 15),
        amount=Decimal("-25.00"),
        merchant_raw="TUDOR LOCAL",
        merchant_clean="TUDOR LOCAL",
        category_ynab="Groceries",
        category_dashboard="Other",
        category_source="other",
        ynab_approved=True,
        is_transfer=False,
    )
    db_session.add(tx)
    await db_session.flush()  # flush not commit
    await db_session.refresh(tx)

    response = await client.patch(
        f"/api/v1/transactions/{tx.id}/category",
        json={
            "category": "Groceries",
            "save_as_merchant_rule": False,
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["category_dashboard"] == "Groceries"
    assert data["category_source"] == "manual_override"


async def test_patch_transaction_saves_merchant_rule(client, db_session):
    from app.models.transaction import Transaction
    from app.models.merchant_override import MerchantOverride
    from datetime import date
    from decimal import Decimal
    from sqlalchemy import select

    tx = Transaction(
        ynab_transaction_id=f"test-{uuid.uuid4()}",
        date=date(2024, 1, 15),
        amount=Decimal("-12.50"),
        merchant_raw="BROOKWOOD FOOD",
        merchant_clean="BROOKWOOD FOOD",
        category_ynab="",
        category_dashboard="Other",
        category_source="other",
        ynab_approved=True,
        is_transfer=False,
    )
    db_session.add(tx)
    await db_session.flush()  # flush not commit
    await db_session.refresh(tx)

    response = await client.patch(
        f"/api/v1/transactions/{tx.id}/category",
        json={
            "category": "Groceries",
            "save_as_merchant_rule": True,
        }
    )

    assert response.status_code == 200

    result = await db_session.execute(
        select(MerchantOverride).where(
            MerchantOverride.merchant_clean == "BROOKWOOD FOOD"
        )
    )
    override = result.scalar_one_or_none()
    assert override is not None
    assert override.category_dashboard == "Groceries"


async def test_patch_nonexistent_transaction_returns_404(client, db_session):
    response = await client.patch(
        f"/api/v1/transactions/{uuid.uuid4()}/category",
        json={"category": "Groceries", "save_as_merchant_rule": False}
    )
    assert response.status_code == 404


async def test_list_transactions_returns_all(client, db_session):
    from app.models.transaction import Transaction
    from datetime import date
    from decimal import Decimal

    # Create two test transactions
    for merchant in ["Tesco", "Costa Coffee"]:
        tx = Transaction(
            ynab_transaction_id=f"test-{uuid.uuid4()}",
            date=date(2024, 1, 15),
            amount=Decimal("-25.00"),
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

    response = await client.get("/api/v1/transactions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


async def test_list_transactions_filters_by_category(client, db_session):
    from app.models.transaction import Transaction
    from datetime import date
    from decimal import Decimal

    for category in ["Groceries", "Eating Out"]:
        tx = Transaction(
            ynab_transaction_id=f"test-{uuid.uuid4()}",
            date=date(2024, 1, 15),
            amount=Decimal("-25.00"),
            merchant_raw="Test Merchant",
            merchant_clean="Test Merchant",
            category_ynab=category,
            category_dashboard=category,
            category_source="ynab",
            ynab_approved=True,
            is_transfer=False,
        )
        db_session.add(tx)
    await db_session.flush()

    response = await client.get(
        "/api/v1/transactions",
        params={"categories": ["Groceries"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category_dashboard"] == "Groceries"


async def test_list_transactions_filters_by_date_range(client, db_session):
    from app.models.transaction import Transaction
    from datetime import date
    from decimal import Decimal

    for tx_date in [date(2024, 1, 15), date(2024, 3, 15)]:
        tx = Transaction(
            ynab_transaction_id=f"test-{uuid.uuid4()}",
            date=tx_date,
            amount=Decimal("-25.00"),
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
        "/api/v1/transactions",
        params={"from_date": "2024-01-01", "to_date": "2024-02-01"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["date"] == "2024-01-15"


async def test_get_single_transaction(client, db_session):
    from app.models.transaction import Transaction
    from datetime import date
    from decimal import Decimal

    tx = Transaction(
        ynab_transaction_id=f"test-{uuid.uuid4()}",
        date=date(2024, 1, 15),
        amount=Decimal("-25.00"),
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
    await db_session.refresh(tx)

    response = await client.get(f"/api/v1/transactions/{tx.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["merchant_clean"] == "Tesco"
    assert data["category_dashboard"] == "Groceries"


async def test_get_nonexistent_transaction_returns_404(client, db_session):
    response = await client.get(f"/api/v1/transactions/{uuid.uuid4()}")
    assert response.status_code == 404