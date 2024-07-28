import datetime
from collections.abc import Sequence

import pytest
import pytest_asyncio
import sqlalchemy as sa
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from componentsdb import auth
from componentsdb.db import models as dbm


@pytest.fixture
def token_user(faker: Faker, users: Sequence[dbm.User]) -> dbm.User:
    return faker.random_element(users)


@pytest_asyncio.fixture
async def access_token(
    token_user: dbm.User,
    db_session: AsyncSession,
    authentication_provider: auth.AuthenticationProvider,
) -> dbm.AccessToken:
    credentials = await authentication_provider.create_user_credentials(token_user)
    return (
        await db_session.execute(
            sa.select(dbm.AccessToken).where(dbm.AccessToken.token == credentials.access_token)
        )
    ).scalar_one()


@pytest.mark.asyncio
async def test_create_access_token(token_user: dbm.User, access_token: dbm.AccessToken):
    assert access_token.token is not None
    assert len(access_token.token) > 0
    assert access_token.user_id == token_user.id
    assert access_token.expires_at is not None
    assert access_token.expires_at > datetime.datetime.now(datetime.UTC)


@pytest.mark.asyncio
async def test_invalid_access_token(
    faker: Faker, authentication_provider: auth.AuthenticationProvider
):
    with pytest.raises(auth.InvalidAccessTokenError):
        await authentication_provider.authenticate_user_from_access_token(faker.slug())


@pytest.mark.asyncio
async def test_expired_access_token(
    faker: Faker,
    db_session: AsyncSession,
    access_token: dbm.AccessToken,
    authentication_provider: auth.AuthenticationProvider,
):
    access_token.expires_at = faker.past_datetime()
    db_session.add(access_token)
    await db_session.flush([access_token])

    with pytest.raises(auth.InvalidAccessTokenError):
        await authentication_provider.authenticate_user_from_access_token(access_token.token)


@pytest.mark.asyncio
async def test_valid_access_token(
    faker: Faker,
    access_token: dbm.AccessToken,
    token_user: dbm.User,
    authentication_provider: auth.AuthenticationProvider,
):
    user = await authentication_provider.authenticate_user_from_access_token(access_token.token)
    assert user.id == token_user.id
