import pytest

# ---------------------------------------
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import os

os.environ["MODE"] = "TEST"
load_dotenv(".env-test", override=True)

# ---------------------------------------
from src.config import Settings
from src.database import Base, engine_null_pull
from src.utils.db_manager import get_db_manager_null_pull

settings = Settings()


@pytest.fixture(autouse=True)
async def setup_database():
    assert settings.MODE
    async with engine_null_pull.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="function")
async def db():
    async for db in get_db_manager_null_pull():
        yield db
