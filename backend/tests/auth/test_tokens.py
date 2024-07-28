import datetime
from collections.abc import Sequence

import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from componentsdb import auth
from componentsdb.db import models as dbm


@pytest.mark.asyncio
async def test_create_access_token(db_session: AsyncSession, users: Sequence[dbm.User]):
    access_token = auth.create_access_token(db_session, users[0], 200)
    await db_session.flush()
    await db_session.refresh(access_token)
    assert access_token.user_id == users[0].id
    assert access_token.token is not None
    assert len(access_token.token) > 0
    assert access_token.expires_at is not None
    assert access_token.expires_at > datetime.datetime.now(datetime.UTC)


@pytest.mark.asyncio
async def test_create_refresh_token(db_session: AsyncSession, users: Sequence[dbm.User]):
    refresh_token = auth.create_refresh_token(db_session, users[0], 200)
    await db_session.flush()
    await db_session.refresh(refresh_token)
    assert refresh_token.user_id == users[0].id
    assert refresh_token.token is not None
    assert len(refresh_token.token) > 0
    assert refresh_token.expires_at is not None
    assert refresh_token.expires_at > datetime.datetime.now(datetime.UTC)


@pytest.mark.asyncio
async def test_user_from_federated_credential_claims(
    db_session: AsyncSession, federated_user_credentials: Sequence[dbm.FederatedUserCredential]
):
    u = await auth.user_from_federated_credential_claims(
        db_session,
        {
            "aud": federated_user_credentials[0].audience,
            "iss": federated_user_credentials[0].issuer,
            "sub": federated_user_credentials[0].subject,
        },
    )
    assert u.id == federated_user_credentials[0].user_id


@pytest.mark.asyncio
async def test_user_from_federated_credential_claims_no_such_user(
    faker: Faker,
    db_session: AsyncSession,
    federated_user_credentials: Sequence[dbm.FederatedUserCredential],
):
    with pytest.raises(auth.NoSuchUser):
        await auth.user_from_federated_credential_claims(
            db_session,
            {
                "aud": faker.url(schemes=["https"]),
                "iss": federated_user_credentials[0].issuer,
                "sub": federated_user_credentials[0].subject,
            },
        )


@pytest.mark.asyncio
async def test_user_from_federated_credential_claims_create_user(
    faker: Faker,
    db_session: AsyncSession,
    federated_user_credentials: Sequence[dbm.FederatedUserCredential],
):
    u = await auth.user_from_federated_credential_claims(
        db_session,
        {
            "aud": faker.url(schemes=["https"]),
            "iss": federated_user_credentials[0].issuer,
            "sub": federated_user_credentials[0].subject,
        },
        create_if_not_present=True,
    )
    assert u is not None
    assert u.id != 0


@pytest.mark.asyncio
async def test_no_user_for_invalid_access_token(
    faker: Faker, authentication_provider: auth.AuthenticationProvider
):
    with pytest.raises(auth.InvalidAccessTokenError):
        await authentication_provider.authenticate_user_from_access_token(faker.slug())


@pytest.mark.asyncio
async def test_no_user_for_expired_access_token(
    faker: Faker,
    users: list[dbm.User],
    db_session: AsyncSession,
    authentication_provider: auth.AuthenticationProvider,
):
    user = users[0]
    access_token = auth.create_access_token(db_session, user, 500)
    await db_session.flush([access_token])

    u = await authentication_provider.authenticate_user_from_access_token(access_token.token)
    assert u.id == user.id

    access_token.expires_at = faker.past_datetime()
    db_session.add(access_token)
    await db_session.flush([access_token])

    with pytest.raises(auth.InvalidAccessTokenError):
        await authentication_provider.authenticate_user_from_access_token(access_token.token)
