import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from componentsdb import auth


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
