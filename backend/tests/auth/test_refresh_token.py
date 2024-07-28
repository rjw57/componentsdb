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
async def refresh_token(
    token_user: dbm.User,
    db_session: AsyncSession,
    authentication_provider: auth.AuthenticationProvider,
) -> dbm.RefreshToken:
    credentials = await authentication_provider.create_user_credentials(token_user)
    return (
        await db_session.execute(
            sa.select(dbm.RefreshToken).where(dbm.RefreshToken.token == credentials.refresh_token)
        )
    ).scalar_one()


@pytest.mark.asyncio
async def test_create_refresh_token(token_user: dbm.User, refresh_token: dbm.RefreshToken):
    assert refresh_token.token is not None
    assert len(refresh_token.token) > 0
    assert refresh_token.user_id == token_user.id
    assert refresh_token.expires_at is not None
    assert refresh_token.expires_at > datetime.datetime.now(datetime.UTC)
    assert refresh_token.used_at is None


@pytest.mark.asyncio
async def test_invalid_refresh_token(
    faker: Faker, authentication_provider: auth.AuthenticationProvider
):
    with pytest.raises(auth.InvalidRefreshTokenError):
        await authentication_provider.user_credentials_from_refresh_token(faker.slug())


@pytest.mark.asyncio
async def test_expired_refresh_token(
    faker: Faker,
    db_session: AsyncSession,
    refresh_token: dbm.RefreshToken,
    authentication_provider: auth.AuthenticationProvider,
):
    refresh_token.expires_at = faker.past_datetime()
    db_session.add(refresh_token)
    await db_session.flush([refresh_token])

    with pytest.raises(auth.InvalidRefreshTokenError):
        await authentication_provider.user_credentials_from_refresh_token(refresh_token.token)


@pytest.mark.asyncio
async def test_used_refresh_token(
    faker: Faker,
    token_user: dbm.User,
    refresh_token: dbm.RefreshToken,
    db_session: AsyncSession,
    authentication_provider: auth.AuthenticationProvider,
):
    credentials = await authentication_provider.user_credentials_from_refresh_token(
        refresh_token.token
    )
    assert credentials.user.id == token_user.id

    await db_session.refresh(refresh_token)
    assert refresh_token.used_at is not None

    with pytest.raises(auth.InvalidRefreshTokenError):
        await authentication_provider.user_credentials_from_refresh_token(refresh_token.token)
