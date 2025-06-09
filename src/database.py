import asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

import sys
from pathlib import Path

# добавление src в поле видимости
sys.path.append(str(Path(__file__).parent.parent))

from src.config import settings


engine = create_async_engine(url=settings.DB_URL)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=True)

class Base(DeclarativeBase) :
    pass

