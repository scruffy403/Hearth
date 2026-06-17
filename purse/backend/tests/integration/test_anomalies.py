import pytest
import uuid
from datetime import date
from decimal import Decimal


async def test_anomalies_flags_unusually_large_transaction(client, db_session):
    from app.models.transaction import Transaction

    # Normal grocery transactions clustered around £30-50
    normal_amounts = [Decimal("-30.00"), Decimal("-35.00"), Decimal("-40.00"),
                       Decimal("-32.00"), Decimal("-38.00"), Decimal("-45.00")]
    for amount in normal_amounts:
        tx = Transaction(
            ynab_transaction_id=f"test-{uuid.uuid4()}",
            date=date(2024, 1, 15),
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

    # One anomalously large transaction
    outlier = Transaction(
        ynab_transaction_id=f"test-{uuid.uuid4()}",
        date=date(2024, 1, 20),
        amount=Decimal("-450.00"),
        merchant_raw="Tesco",
        merchant_clean="Tesco",
        category_ynab="Groceries",
        category_dashboard="Groceries",
        category_source="ynab",
        ynab_approved=True,
        is_transfer=False,
    )
    db_session.add(outlier)
    await db_session.flush()

    response = await client.get("/api/v1/anomalies")
    assert response.status_code == 200
    data = response.json()

    flagged_amounts = [a["amount"] for a in data]
    assert -450.00 in flagged_amounts


async def test_anomalies_does_not_flag_normal_transactions(client, db_session):
    from app.models.transaction import Transaction

    # Tight cluster, no outliers
    amounts = [Decimal("-30.00"), Decimal("-31.00"), Decimal("-29.00"),
               Decimal("-32.00"), Decimal("-30.50"), Decimal("-29.50")]
    for amount in amounts:
        tx = Transaction(
            ynab_transaction_id=f"test-{uuid.uuid4()}",
            date=date(2024, 1, 15),
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

    response = await client.get("/api/v1/anomalies")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0