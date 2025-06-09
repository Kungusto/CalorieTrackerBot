import asyncio

import sys
from pathlib import Path

# добавление src в поле видимости
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.repositories.users import UsersRepository
from src.database import async_session_maker_null_pull, async_session_maker

class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        
    async def __aenter__(self): 
        self.session = self.session_factory()
        
        self.users = UsersRepository(self.session)

        return self

    async def __aexit__(self, *args): 
        await self.session.rollback()
        await self.session.close()
    
    async def commit(self):
        await self.session.commit()

async def get_db_manager():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db
 
async def get_db_manager_null_pull() :
    async with DBManager(session_factory=async_session_maker_null_pull) as db:
        yield db
