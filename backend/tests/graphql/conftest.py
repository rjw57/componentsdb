import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from componentsdb.graphql import make_context


@pytest.fixture
def context(db_session: AsyncSession):
    return make_context(db_session)
