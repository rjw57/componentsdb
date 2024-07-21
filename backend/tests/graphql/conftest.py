import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from componentsdb.graphql.schema import context_from_db_session


@pytest.fixture
def context(db_session: AsyncSession):
    return context_from_db_session(db_session)
