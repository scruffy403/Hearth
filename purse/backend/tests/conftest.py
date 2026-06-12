# tests/conftest.py — shared fixtures, NO database setup here
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import get_db


@pytest.fixture
async def client(db_session):
    """AsyncClient with DB dependency overridden to use test session."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()