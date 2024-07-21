import contextlib

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession


@contextlib.contextmanager
def expected_sql_query_count(db_session: AsyncSession, expected_count: int):
    state = {"count": 0}

    def on_do_orm_execute(orm_execute_state):
        state["count"] += 1

    event.listen(db_session.sync_session, "do_orm_execute", on_do_orm_execute)
    yield
    event.remove(db_session.sync_session, "do_orm_execute", on_do_orm_execute)
    assert (
        expected_count == state["count"]
    ), f"Unexpected number of SQL queries. Expected: {expected_count}, actual: {state['count']}"
