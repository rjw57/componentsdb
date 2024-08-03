import contextlib
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


@contextlib.asynccontextmanager
async def db_session(sqlalchemy_db_url: str) -> AsyncGenerator[AsyncSession, None]:
    db_engine = create_async_engine(sqlalchemy_db_url)
    session_maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with session_maker.begin() as session:
        yield session
