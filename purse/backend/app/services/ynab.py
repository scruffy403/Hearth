from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

import httpx

from app.config import settings


YNAB_BASE_URL = "https://api.ynab.com/v1"


class YNABClient:
    """
    Async HTTP client for the YNAB API.
    Handles authentication and raw API calls.
    """

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = YNAB_BASE_URL

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    async def get_transactions(
        self,
        budget_id: str,
        since_date: str,
    ) -> list[dict[str, Any]]:
        """
        Fetch transactions since a given date.

        Args:
            budget_id:  YNAB budget UUID
            since_date: ISO date string 'YYYY-MM-DD'

        Returns:
            List of raw YNAB transaction dicts
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/budgets/{budget_id}/transactions",
                headers=self._headers(),
                params={"since_date": since_date},
                timeout=20,
            )
            response.raise_for_status()
            data = response.json().get("data", {})
            return data.get("transactions", [])

    async def get_categories(
        self,
        budget_id: str,
    ) -> list[dict[str, Any]]:
        """
        Fetch all category groups with their categories.

        Returns:
            List of category group dicts, each containing a 'categories' list
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/budgets/{budget_id}/categories",
                headers=self._headers(),
                timeout=15,
            )
            response.raise_for_status()
            data = response.json().get("data", {})
            return data.get("category_groups", [])

    async def get_payees(
        self,
        budget_id: str,
    ) -> list[dict[str, Any]]:
        """
        Fetch all payees for a budget.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/budgets/{budget_id}/payees",
                headers=self._headers(),
                timeout=15,
            )
            response.raise_for_status()
            data = response.json().get("data", {})
            return data.get("payees", [])

    async def get_budgets(self) -> list[dict[str, Any]]:
        """
        List all budgets accessible with the current API key.
        Useful for verifying credentials and finding budget IDs.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/budgets",
                headers=self._headers(),
                timeout=15,
            )
            response.raise_for_status()
            data = response.json().get("data", {})
            return data.get("budgets", [])


class YNABService:
    """
    Orchestrates YNAB data fetching, normalisation, and database sync.
    Uses YNABClient for HTTP calls and PayeeNormalizer + CategorizationService
    for processing.
    """

    def __init__(self) -> None:
        self.client = YNABClient(api_key=settings.ynab_api_key)
        self.budget_id = settings.ynab_budget_id

    # ------------------------------------------------------------------
    # Unit-testable helper methods
    # ------------------------------------------------------------------

    def _parse_date(self, date_string: str) -> date:
        """
        Convert a YNAB date string to a Python date object.
        YNAB returns dates as 'YYYY-MM-DD' strings; asyncpg requires
        a proper date object for DATE column inserts.
        """
        return date.fromisoformat(date_string)

    def _milliunit_to_decimal(self, amount_milli: int) -> Decimal:
        """
        Convert YNAB milliunits to a Decimal amount.
        YNAB stores amounts as integers in thousandths:
        -45000 milliunits = -45.00 GBP
        """
        return Decimal(amount_milli) / Decimal(1000)

    def _is_transfer(self, transaction: dict[str, Any]) -> bool:
        """
        A transaction is a transfer if YNAB has linked it to
        another account via transfer_account_id.
        """
        return bool(transaction.get("transfer_account_id"))

    def _get_lookback_date(self, days: int) -> str:
        """
        Return an ISO date string N days in the past.
        """
        return (date.today() - timedelta(days=days)).isoformat()

    def _build_category_lookup(
        self,
        category_groups: list[dict[str, Any]],
    ) -> dict[str, str]:
        """
        Flatten YNAB category groups into a dict of category_id -> category_name.
        """
        lookup: dict[str, str] = {}
        for group in category_groups:
            for category in group.get("categories", []):
                cid = category.get("id")
                cname = category.get("name", "")
                if cid:
                    lookup[cid] = cname
        return lookup

    # ------------------------------------------------------------------
    # Sync orchestration — will be called by APScheduler
    # ------------------------------------------------------------------

    async def sync_transactions(
            self,
            db: AsyncSession,
    ) -> dict[str, Any]:
        """
        Fetch recent transactions from YNAB and upsert into the database.
        Uses ynab_transaction_id as the unique key — safe to run repeatedly.

        Args:
            db: AsyncSession injected from the router or scheduler

        Returns:
            Summary dict with counts and any errors
        """
        from sqlalchemy import select
        from sqlalchemy.dialects.postgresql import insert

        from app.models.transaction import Transaction
        from app.services.payee_normalizer import PayeeNormalizer
        from app.services.categorization import CategorizationService
        from app.models.merchant_override import MerchantOverride

        normalizer = PayeeNormalizer()

        # Load merchant overrides from DB for categorisation
        override_rows = await db.execute(select(MerchantOverride))
        overrides = {
            row.merchant_clean: row.category_dashboard
            for row in override_rows.scalars().all()
        }

        categorizer = CategorizationService(overrides=overrides)

        # Fetch from YNAB
        since_date = self._get_lookback_date(days=settings.ynab_lookback_days)
        raw_transactions = await self.client.get_transactions(
            budget_id=self.budget_id,
            since_date=since_date,
        )
        category_groups = await self.client.get_categories(
            budget_id=self.budget_id
        )
        category_lookup = self._build_category_lookup(category_groups)

        results: dict[str, Any] = {
            "fetched": len(raw_transactions),
            "synced": 0,
            "skipped_transfers": 0,
            "errors": [],
        }

        for tx in raw_transactions:
            try:
                if self._is_transfer(tx):
                    results["skipped_transfers"] += 1
                    continue

                merchant_raw = tx.get("payee_name") or ""
                merchant_clean = normalizer.normalize(merchant_raw)
                amount = self._milliunit_to_decimal(tx.get("amount", 0))
                category_ynab = category_lookup.get(
                    tx.get("category_id", ""), ""
                ).strip()

                # Categorise
                cat_result = categorizer.categorize(
                    merchant_clean=merchant_clean,
                    ynab_category=category_ynab,
                    amount=float(amount),
                )

                # Upsert — insert or update on conflict with ynab_transaction_id
                stmt = insert(Transaction).values(
                    ynab_transaction_id=tx["id"],
                    date=self._parse_date(tx["date"]),
                    amount=amount,
                    currency="GBP",
                    merchant_raw=merchant_raw,
                    merchant_clean=merchant_clean,
                    category_ynab=category_ynab,
                    category_dashboard=cat_result.category,
                    category_source=cat_result.source,
                    ml_confidence=None,
                    ynab_approved=tx.get("approved", False),
                    is_transfer=False,
                    notes=tx.get("memo"),
                ).on_conflict_do_update(
                    index_elements=["ynab_transaction_id"],
                    set_=dict(
                        merchant_clean=merchant_clean,
                        category_ynab=category_ynab,
                        category_dashboard=cat_result.category,
                        category_source=cat_result.source,
                        ynab_approved=tx.get("approved", False),
                        notes=tx.get("memo"),
                    ),
                )
                await db.execute(stmt)
                results["synced"] += 1

            except Exception as e:
                results["errors"].append(
                    {"transaction_id": tx.get("id"), "error": str(e)}
                )

        await db.commit()
        return results

    async def get_oldest_transaction_date(self) -> str | None:
        """
        Fetch all transactions and return the date of the oldest one.
        Useful for understanding how much historical data YNAB holds.
        """
        raw = await self.client.get_transactions(
            budget_id=self.budget_id,
            since_date="2010-01-01",
        )
        if not raw:
            return None
        dates = [tx.get("date") for tx in raw if tx.get("date")]
        return min(dates) if dates else None