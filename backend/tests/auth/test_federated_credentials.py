import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from componentsdb import auth
from componentsdb.db import models as dbm


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
    faker: Faker,
    federated_identity_provider_name: str,
    make_oidc_token,
    oidc_claims,
    authentication_provider: auth.AuthenticationProvider,
):
    def new_token():
        return make_oidc_token({**oidc_claims, "jti": faker.uuid4()})

    with pytest.raises(auth.NoSuchUser):
        await authentication_provider.user_credentials_from_federated_credential(
            federated_identity_provider_name, new_token()
        )

    credentials = await authentication_provider.create_user_from_federated_credential(
        federated_identity_provider_name, new_token()
    )

    authenticated_user = await authentication_provider.authenticate_user_from_access_token(
        credentials.access_token
    )
    assert authenticated_user.id == credentials.user.id


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


@pytest.mark.asyncio
async def test_can_reuse_credentials_with_no_jti(
    federated_identity_provider_name: str,
    federated_credential_user: dbm.User,
    make_oidc_token,
    oidc_claims,
    authentication_provider: auth.AuthenticationProvider,
):
    claims = {**oidc_claims}
    del claims["jti"]
    token = make_oidc_token(claims)

    credentials = await authentication_provider.user_credentials_from_federated_credential(
        federated_identity_provider_name, token
    )
    assert credentials.user.id == federated_credential_user.id

    authenticated_user = await authentication_provider.authenticate_user_from_access_token(
        credentials.access_token
    )
    assert authenticated_user.id == credentials.user.id

    credentials = await authentication_provider.user_credentials_from_federated_credential(
        federated_identity_provider_name, token
    )
    assert credentials.user.id == federated_credential_user.id


@pytest.mark.asyncio
async def test_cannot_reuse_credentials_with_jti(
    federated_identity_provider_name: str,
    federated_credential_user: dbm.User,
    make_oidc_token,
    oidc_claims,
    authentication_provider: auth.AuthenticationProvider,
):
    assert "jti" in oidc_claims
    token = make_oidc_token(oidc_claims)

    credentials = await authentication_provider.user_credentials_from_federated_credential(
        federated_identity_provider_name, token
    )
    assert federated_credential_user.id == credentials.user.id

    with pytest.raises(auth.InvalidFederatedCredential):
        await authentication_provider.user_credentials_from_federated_credential(
            federated_identity_provider_name, token
        )


@pytest.mark.asyncio
async def test_credendial_not_jwt(
    faker: Faker,
    authentication_provider: auth.AuthenticationProvider,
    federated_identity_provider_name: str,
):
    with pytest.raises(auth.InvalidFederatedCredential):
        await authentication_provider.user_credentials_from_federated_credential(
            federated_identity_provider_name, faker.slug()
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("missing_claim", ["iss", "aud", "exp", "sub"])
async def test_credendial_missing_required_claim(
    missing_claim: str,
    authentication_provider: auth.AuthenticationProvider,
    federated_identity_provider_name: str,
    oidc_claims,
    make_oidc_token,
):
    claims = {**oidc_claims}
    del claims["iss"]
    with pytest.raises(auth.InvalidFederatedCredential):
        await authentication_provider.user_credentials_from_federated_credential(
            federated_identity_provider_name, make_oidc_token(claims)
        )


@pytest.mark.asyncio
async def test_credendial_payload_not_dict(
    authentication_provider: auth.AuthenticationProvider,
    federated_identity_provider_name: str,
    make_oidc_token,
):
    with pytest.raises(auth.InvalidFederatedCredential):
        await authentication_provider.user_credentials_from_federated_credential(
            federated_identity_provider_name, make_oidc_token("not a dict")
        )
