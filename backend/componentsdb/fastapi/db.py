import structlog
from fastapi import Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .settings import Settings, load_settings

LOG = structlog.get_logger()


async def get_db_session(settings: Settings = Depends(load_settings)):
    db_engine = create_async_engine(settings.sqlalchemy_db_url)
    session_maker = async_sessionmaker(db_engine, expire_on_commit=False)

    stats = {"statementCount": 0}

    def on_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        stats["statementCount"] += 1

    async with session_maker.begin() as session:
        event.listen(db_engine.sync_engine, "before_cursor_execute", on_before_cursor_execute)
        try:
            yield session
            await session.flush()
        except HTTPException as e:
            LOG.info(
                "Rolling back database session because of HTTP exception",
                stats=stats,
                status_code=e.status_code,
                detail=e.detail,
            )
            await session.rollback()
            raise e
        except Exception as e:
            LOG.exception(
                "Rolling back database session because of unexpected exception.", stats=stats
            )
            await session.rollback()
            raise e
        else:
            LOG.info("Committing database session", stats=stats)
            await session.commit()
        finally:
            event.remove(db_engine.sync_engine, "before_cursor_execute", on_before_cursor_execute)
