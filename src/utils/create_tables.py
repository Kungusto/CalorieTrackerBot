import asyncio

import sys
from pathlib import Path

# добавление src в поле видимости
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.database import Base, engine
from src.models import *

async def create_tables():
    async with engine.begin() as conn :
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(create_tables())