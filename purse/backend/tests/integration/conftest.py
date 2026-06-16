import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from httpx import AsyncClient, ASGITransport

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "postgresql+asyncpg://hearth:hearth@postgres:5432/hearth_purse_test"


@pytest.fixture
async def db_engine():
    """Fresh engine per test — avoids asyncpg event loop conflicts."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()