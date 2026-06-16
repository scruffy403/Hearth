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