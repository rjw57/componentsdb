from collections.abc import Sequence
from typing import Any

import pytest
import pytest_asyncio
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from componentsdb import auth
from componentsdb.db import fakes
from componentsdb.db import models as dbm


@pytest_asyncio.fixture
async def federated_credential_user(
    faker: Faker, db_session: AsyncSession, users: Sequence[dbm.User], oidc_claims: dict[str, Any]
) -> dbm.User:
    user = faker.random_element(users)
    fed_cred = fakes.fake_federated_user_credential(faker, user)
    fed_cred.audience = oidc_claims["aud"]
    fed_cred.issuer = oidc_claims["iss"]
    fed_cred.subject = oidc_claims["sub"]
    db_session.add(fed_cred)
    await db_session.flush([fed_cred])
    return user


@pytest.mark.asyncio
async def test_user_credentials_from_federated_credential(
    db_session: AsyncSession,
    federated_credential_user: dbm.User,
    federated_identity_provider_name: str,
    oidc_token: str,
    authentication_provider: auth.AuthenticationProvider,
):
    credentials = await authentication_provider.user_credentials_from_federated_credential(
        federated_identity_provider_name, oidc_token
    )
    assert credentials.user.id == federated_credential_user.id

    user = await authentication_provider.authenticate_user_from_access_token(
        credentials.access_token
    )
    assert user.id == federated_credential_user.id

    new_credentials = await authentication_provider.user_credentials_from_refresh_token(
        credentials.refresh_token
    )
    assert new_credentials.user.id == federated_credential_user.id

    user = await authentication_provider.authenticate_user_from_access_token(
        credentials.access_token
    )
    assert user.id == federated_credential_user.id


@pytest.mark.asyncio
async def test_no_such_provider(
    faker: Faker,
    oidc_token: str,
    authentication_provider: auth.AuthenticationProvider,
):
    with pytest.raises(auth.InvalidProvider):
        await authentication_provider.user_credentials_from_federated_credential(
            faker.slug(), oidc_token
        )


@pytest.mark.asyncio
async def test_no_matching_user(
    oidc_token: str,
    authentication_provider: auth.AuthenticationProvider,
    federated_identity_provider_name: str,
):
    with pytest.raises(auth.NoSuchUser):
        await authentication_provider.user_credentials_from_federated_credential(
            federated_identity_provider_name, oidc_token
        )


@pytest.mark.asyncio
async def test_create_user_from_federated_credential(
    federated_identity_provider_name: str,
    oidc_token: str,
    authentication_provider: auth.AuthenticationProvider,
):
    with pytest.raises(auth.NoSuchUser):
        await authentication_provider.user_credentials_from_federated_credential(
            federated_identity_provider_name, oidc_token
        )

    user = await authentication_provider.create_user_from_federated_credential(
        federated_identity_provider_name, oidc_token
    )

    credentials = await authentication_provider.user_credentials_from_federated_credential(
        federated_identity_provider_name, oidc_token
    )
    assert credentials.user.id == user.id

    authenticated_user = await authentication_provider.authenticate_user_from_access_token(
        credentials.access_token
    )
    assert authenticated_user.id == user.id


@pytest.mark.asyncio
async def test_create_user_from_federated_credential_existing_user(
    federated_identity_provider_name: str,
    oidc_token: str,
    authentication_provider: auth.AuthenticationProvider,
    federated_credential_user: dbm.User,
):
    with pytest.raises(auth.UserAlreadySignedUp):
        await authentication_provider.create_user_from_federated_credential(
            federated_identity_provider_name, oidc_token
        )
