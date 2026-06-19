"""
Regression tests for the sync upsert logic preserving ml/manual_override
category sources rather than blindly overwriting them on every sync run.

Background: sync_transactions previously used a plain on_conflict_do_update
that always set category_dashboard/category_source/ml_confidence to
whatever the rule-based categorizer decided on that run. Since ML and
manual_override categorisations exist precisely for transactions the
rule-based categorizer can't handle, re-running sync would silently reset
those transactions back to 'Other' on the next run — this is how the
Phase 3 ML categorisations got wiped.
"""
import uuid
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select

from app.models.transaction import Transaction
from app.services.ynab import YNABService


def _make_raw_ynab_transaction(
    tx_id: str,
    merchant: str = "Test Merchant",
    amount_milli: int = -5000,
    category_name: str = "",
    tx_date: str = "2026-01-15",
) -> dict:
    return {
        "id": tx_id,
        "date": tx_date,
        "amount": amount_milli,
        "payee_name": merchant,
        "category_id": "cat-1" if category_name else "",
        "approved": True,
        "memo": None,
        "transfer_account_id": None,
    }


@pytest.fixture
def ynab_service() -> YNABService:
    service = YNABService()
    return service


async def test_sync_does_not_overwrite_existing_ml_categorisation(
    db_session, ynab_service
):
    """
    A transaction previously categorised by the ML model (source='ml')
    must keep its category_dashboard/category_source/ml_confidence
    untouched when the same transaction is synced again, even though
    the rule-based categorizer would otherwise reset it to 'Other'.
    """
    tx_id = f"ynab-{uuid.uuid4()}"

    existing = Transaction(
        ynab_transaction_id=tx_id,
        date=date(2026, 1, 15),
        amount=Decimal("-5.00"),
        currency="GBP",
        merchant_raw="Test Merchant",
        merchant_clean="Test Merchant",
        category_ynab="",
        category_dashboard="Pets",
        category_source="ml",
        ml_confidence=Decimal("0.87"),
        ynab_approved=True,
        is_transfer=False,
    )
    db_session.add(existing)
    await db_session.flush()

    raw_tx = _make_raw_ynab_transaction(tx_id, merchant="Test Merchant")

    with patch.object(
        ynab_service.client, "get_transactions", new=AsyncMock(return_value=[raw_tx])
    ), patch.object(
        ynab_service.client, "get_categories", new=AsyncMock(return_value=[])
    ):
        await ynab_service.sync_transactions(db=db_session, ml_service=None)

    # Force a real re-fetch — see the comment in
    # test_sync_still_updates_ynab_sourced_transactions for why this
    # matters: without it, this test would pass even if the preservation
    # logic were broken, since it'd just be reading back the same
    # in-memory object created at the top of the test.
    db_session.expire_all()

    result = await db_session.execute(
        select(Transaction).where(Transaction.ynab_transaction_id == tx_id)
    )
    updated = result.scalar_one()

    assert updated.category_dashboard == "Pets"
    assert updated.category_source == "ml"
    assert updated.ml_confidence == Decimal("0.87")


async def test_sync_does_not_overwrite_manual_override(db_session, ynab_service):
    """
    A transaction a person has manually recategorised (source='manual_override')
    must keep that category on subsequent syncs.
    """
    tx_id = f"ynab-{uuid.uuid4()}"

    existing = Transaction(
        ynab_transaction_id=tx_id,
        date=date(2026, 1, 15),
        amount=Decimal("-12.00"),
        currency="GBP",
        merchant_raw="Ambiguous Merchant",
        merchant_clean="Ambiguous Merchant",
        category_ynab="",
        category_dashboard="Gifts",
        category_source="manual_override",
        ml_confidence=None,
        ynab_approved=True,
        is_transfer=False,
    )
    db_session.add(existing)
    await db_session.flush()

    raw_tx = _make_raw_ynab_transaction(tx_id, merchant="Ambiguous Merchant")

    with patch.object(
        ynab_service.client, "get_transactions", new=AsyncMock(return_value=[raw_tx])
    ), patch.object(
        ynab_service.client, "get_categories", new=AsyncMock(return_value=[])
    ):
        await ynab_service.sync_transactions(db=db_session, ml_service=None)

    db_session.expire_all()

    result = await db_session.execute(
        select(Transaction).where(Transaction.ynab_transaction_id == tx_id)
    )
    updated = result.scalar_one()

    assert updated.category_dashboard == "Gifts"
    assert updated.category_source == "manual_override"


async def test_sync_still_updates_ynab_sourced_transactions(db_session, ynab_service):
    """
    A transaction previously categorised straight from YNAB (source='ynab')
    is safe to recompute on each sync — e.g. if the person changes the
    category in YNAB itself, the next sync should pick that up.
    """
    tx_id = f"ynab-{uuid.uuid4()}"

    existing = Transaction(
        ynab_transaction_id=tx_id,
        date=date(2026, 1, 15),
        amount=Decimal("-30.00"),
        currency="GBP",
        merchant_raw="Tesco",
        merchant_clean="Tesco",
        category_ynab="Old Category",
        category_dashboard="Other",
        category_source="ynab",
        ml_confidence=None,
        ynab_approved=True,
        is_transfer=False,
    )
    db_session.add(existing)
    await db_session.flush()

    # This time YNAB reports a real category for the same transaction
    raw_tx = _make_raw_ynab_transaction(
        tx_id, merchant="Tesco", category_name="Groceries"
    )

    with patch.object(
        ynab_service.client, "get_transactions", new=AsyncMock(return_value=[raw_tx])
    ), patch.object(
        ynab_service.client,
        "get_categories",
        new=AsyncMock(
            return_value=[
                {"categories": [{"id": "cat-1", "name": "Groceries"}]}
            ]
        ),
    ):
        await ynab_service.sync_transactions(db=db_session, ml_service=None)

    # The upsert above ran as raw Core SQL (db.execute(stmt)), which does
    # not automatically sync SQLAlchemy's ORM identity map. Without this,
    # the re-query below would return the stale in-memory `existing` object
    # rather than re-reading the row that was actually updated in the
    # database — expire_all() forces a real re-fetch.
    db_session.expire_all()

    result = await db_session.execute(
        select(Transaction).where(Transaction.ynab_transaction_id == tx_id)
    )
    updated = result.scalar_one()

    # category_ynab should reflect the new YNAB category regardless
    assert updated.category_ynab == "Groceries"
    # category_dashboard should now be recomputed since the prior source
    # was 'ynab', not 'ml' or 'manual_override'
    assert updated.category_source in ("ynab", "keyword", "amount", "other")
