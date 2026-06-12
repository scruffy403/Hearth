import pytest
from unittest.mock import AsyncMock, patch


async def test_sync_status_returns_never_synced(client):
    response = await client.get("/api/v1/sync/status")
    assert response.status_code == 200
    data = response.json()
    assert data["last_sync"] is None
    assert data["status"] == "never_synced"


async def test_manual_sync_trigger_returns_accepted(client):
    mock_result = {
        "fetched": 5,
        "synced": 5,
        "skipped_transfers": 0,
        "errors": []
    }
    with patch(
        "app.routers.sync.ynab_service.sync_transactions",
        new_callable=AsyncMock
    ) as mock_sync:
        mock_sync.return_value = mock_result
        response = await client.post("/api/v1/sync/trigger")
        assert response.status_code == 202
        assert response.json()["status"] == "sync_completed"