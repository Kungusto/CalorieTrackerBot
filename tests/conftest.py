import pytest
from src.database import Base, engine


@pytest.fixture(autouse=True)
async def create_tables():
    async with engine.begin() as conn :
        await conn.run_sync(Base.metadata.create_all)