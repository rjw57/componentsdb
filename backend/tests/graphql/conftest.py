from typing import Sequence

import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from componentsdb import auth
from componentsdb.db import models as dbm
from componentsdb.graphql import make_context


@pytest.fixture
def authenticated_user(
    faker: Faker,
    users: Sequence[dbm.User],
) -> dbm.User:
    return faker.random_element(users)


@pytest.fixture
def unauthenticated_context(
    db_session: AsyncSession, authentication_provider: auth.AuthenticationProvider
):
    return make_context(
        db_session=db_session,
        authentication_provider=authentication_provider,
        authenticated_user=None,
    )


@pytest.fixture
def context(
    db_session: AsyncSession,
    authentication_provider: auth.AuthenticationProvider,
    authenticated_user: dbm.User,
):
    return make_context(
        db_session=db_session,
        authentication_provider=authentication_provider,
        authenticated_user=authenticated_user,
    )
