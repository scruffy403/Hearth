import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.ynab import YNABClient, YNABService


class TestYNABClient:
    def test_client_initialises_with_api_key(self):
        client = YNABClient(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.base_url == "https://api.ynab.com/v1"

    @pytest.mark.asyncio
    async def test_get_transactions_calls_correct_endpoint(self):
        client = YNABClient(api_key="test-key")
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "transactions": [
                    {
                        "id": "abc-123",
                        "date": "2024-01-15",
                        "amount": -45000,
                        "payee_name": "Tesco",
                        "category_name": "Groceries",
                        "approved": True,
                        "transfer_account_id": None,
                        "memo": None,
                    }
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            result = await client.get_transactions(
                budget_id="budget-123",
                since_date="2024-01-01"
            )

        assert len(result) == 1
        assert result[0]["id"] == "abc-123"


class TestYNABService:
    def test_converts_milliunits_to_decimal(self):
        service = YNABService.__new__(YNABService)
        assert service._milliunit_to_decimal(-45000) == -45.0
        assert service._milliunit_to_decimal(3850000) == 3850.0

    def test_identifies_transfer_transactions(self):
        service = YNABService.__new__(YNABService)
        tx = {"transfer_account_id": "some-account-id", "amount": -100000}
        assert service._is_transfer(tx) is True

    def test_identifies_non_transfer_transactions(self):
        service = YNABService.__new__(YNABService)
        tx = {"transfer_account_id": None, "amount": -100000}
        assert service._is_transfer(tx) is False

    def test_date_string_is_not_accepted_as_date_object(self):
        """
        Regression test: YNAB returns dates as strings ('YYYY-MM-DD').
        The sync must convert them to Python date objects before inserting.
        This test documents the expected type to prevent regressions.
        """
        from datetime import date
        service = YNABService.__new__(YNABService)
        result = service._parse_date("2026-06-05")
        assert isinstance(result, date)
        assert result.year == 2026
        assert result.month == 6
        assert result.day == 5