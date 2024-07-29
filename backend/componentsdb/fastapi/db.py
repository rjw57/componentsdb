from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .settings import Settings, load_settings


async def get_db_session(settings: Settings = Depends(load_settings)):
    db_engine = create_async_engine(settings.sqlalchemy_db_url)
    session_maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with session_maker.begin() as session:
        try:
            yield session
            await session.flush()
        except Exception as e:
            await session.rollback()
            raise e
        else:
            await session.commit()
