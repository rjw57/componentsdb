import time
from functools import cache

import structlog
from fastapi import Depends, Request
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .settings import Settings, load_settings

LOG = structlog.get_logger()

SLOW_QUERY_THRESHOLD_MS = 100
QUERY_COUNT_THRESHOLD = 10


@cache
def _get_db_session_maker(sqlalchemy_db_url: str):
    db_engine = create_async_engine(load_settings().sqlalchemy_db_url)

    @event.listens_for(db_engine.sync_engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info["query_start_time"] = time.monotonic()

    @event.listens_for(db_engine.sync_engine, "after_cursor_execute")
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

    return async_sessionmaker(db_engine, expire_on_commit=False, autoflush=True)


def get_db_session_maker(settings: Settings = Depends(load_settings)):
    return _get_db_session_maker(settings.sqlalchemy_db_url)


async def get_db_session(request: Request, db_session_maker=Depends(get_db_session_maker)):
    request.state.sql_execution_count = 0

    def on_do_orm_execute(orm_execute_state):
        request.state.sql_execution_count += 1

    async with db_session_maker.begin() as session:
        event.listen(session.sync_session, "do_orm_execute", on_do_orm_execute)
        try:
            yield session
        finally:
            event.remove(session.sync_session, "do_orm_execute", on_do_orm_execute)
        if request.state.sql_execution_count > QUERY_COUNT_THRESHOLD:
            LOG.warn(
                "Executed a large number of SQL queries while handling request.",
                threshold=QUERY_COUNT_THRESHOLD,
                count=request.state.sql_execution_count,
            )
