import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from componentsdb import auth
from componentsdb.graphql import make_context


@pytest.fixture
def context(db_session: AsyncSession, authentication_provider: auth.AuthenticationProvider):
    return make_context(db_session=db_session, authentication_provider=authentication_provider)
