import time

import structlog
from fastapi.exceptions import HTTPException
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .settings import load_settings

LOG = structlog.get_logger()

DB_ENGINE = create_async_engine(load_settings().sqlalchemy_db_url)
SESSION_MAKER = async_sessionmaker(DB_ENGINE, expire_on_commit=False)
SLOW_QUERY_THRESHOLD_MS = 100
QUERY_COUNT_THRESHOLD = 10


@event.listens_for(DB_ENGINE.sync_engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info["query_start_time"] = time.monotonic()


@event.listens_for(DB_ENGINE.sync_engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    query_start_time = conn.info.get("query_start_time", None)
    if query_start_time is None:
        return
    duration_ms = 1e3 * (time.monotonic() - query_start_time)
    if duration_ms > SLOW_QUERY_THRESHOLD_MS:
        LOG.warn(
            "SQL query was slow",
            duration_ms=duration_ms,
            threshold_ms=SLOW_QUERY_THRESHOLD_MS,
            statement=statement,
        )


async def get_db_session():
    stats = {"statement_count": 0}

    def on_do_orm_execute(orm_execute_state):
        stats["statement_count"] += 1

    async with SESSION_MAKER.begin() as session:
        event.listen(session.sync_session, "do_orm_execute", on_do_orm_execute)
        try:
            yield session
            await session.flush()
        except HTTPException as e:
            LOG.warn(
                "Rolling back database session because of HTTP exception",
                status_code=e.status_code,
                detail=e.detail,
            )
            await session.rollback()
            raise e
        except Exception as e:
            LOG.warn("Rolling back database session because of unexpected exception.")
            await session.rollback()
            raise e
        else:
            await session.commit()
        finally:
            event.remove(session.sync_session, "do_orm_execute", on_do_orm_execute)
            if stats["statement_count"] > QUERY_COUNT_THRESHOLD:
                LOG.warn(
                    "Executed a large number of SQL queries while handling request.",
                    threshold=QUERY_COUNT_THRESHOLD,
                    count=stats["statement_count"],
                )
