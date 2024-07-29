from collections.abc import Sequence
from typing import Any

import pytest
import pytest_asyncio
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from componentsdb import auth
from componentsdb.db import fakes
from componentsdb.db import models as dbm


@pytest.fixture
def federated_identity_provider_name(faker: Faker):
    return faker.slug()


@pytest.fixture
def federated_identity_providers(
    federated_identity_provider_name: str,
    oidc_audience: str,
    jwt_issuer: str,
) -> dict[str, auth.FederatedIdentityProvider]:
    return {
        federated_identity_provider_name: auth.FederatedIdentityProvider(
            audience=oidc_audience, issuer=jwt_issuer
        ),
    }


@pytest.fixture
def authentication_provider(
    db_session: AsyncSession,
    federated_identity_providers: dict[str, auth.FederatedIdentityProvider],
) -> auth.AuthenticationProvider:
    return auth.AuthenticationProvider(
        db_session=db_session,
        federated_identity_providers=federated_identity_providers,
    )


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
