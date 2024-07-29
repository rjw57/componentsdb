import pytest
import sqlalchemy as sa
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from componentsdb import auth
from componentsdb.db import models as dbm
from componentsdb.graphql import schema


@pytest.mark.asyncio
async def test_unauthenticated_user(unauthenticated_context):
    query = "query { auth { authenticatedUser { id } } }"
    result = await schema.execute(query, context_value=unauthenticated_context)
    assert result.errors is None
    assert result.data is not None
    assert result.data["auth"]["authenticatedUser"] is None


@pytest.mark.asyncio
async def test_authenticated_user(authenticated_user, context):
    query = "query { auth { authenticatedUser { id email displayName avatarUrl } } }"
    result = await schema.execute(query, context_value=context)
    assert result.errors is None
    assert result.data is not None
    assert result.data["auth"]["authenticatedUser"]["id"] == str(authenticated_user.uuid)
    assert result.data["auth"]["authenticatedUser"]["email"] == authenticated_user.email
    assert (
        result.data["auth"]["authenticatedUser"]["displayName"] == authenticated_user.display_name
    )
    assert result.data["auth"]["authenticatedUser"]["avatarUrl"] == authenticated_user.avatar_url


@pytest.mark.asyncio
async def test_federated_identity_providers(
    federated_identity_provider_name, jwt_issuer, oidc_audience, context
):
    query = "query { auth { federatedIdentityProviders { name audience issuer } } }"
    result = await schema.execute(query, context_value=context)
    assert result.errors is None
    assert result.data is not None
    fips = result.data["auth"]["federatedIdentityProviders"]
    assert len(fips) == 1
    assert fips[0]["name"] == federated_identity_provider_name
    assert fips[0]["issuer"] == jwt_issuer
    assert fips[0]["audience"] == oidc_audience


def assert_credentials_for_user(creds: dict, user: dbm.User):
    assert creds["user"]["id"] == str(user.uuid)
    assert creds["user"]["email"] == user.email
    assert creds["user"]["emailVerified"] == user.email_verified
    assert creds["user"]["displayName"] == user.display_name
    assert creds["user"]["avatarUrl"] == user.avatar_url
    assert creds["accessToken"] is not None
    assert len(creds["accessToken"]) > 0
    assert creds["refreshToken"] is not None
    assert len(creds["refreshToken"]) > 0


@pytest.mark.asyncio
async def test_basic_sign_in(
    federated_identity_provider_name: str,
    oidc_token: str,
    federated_credential_user: dbm.User,
    context,
):
    result = await schema.execute(
        """
        mutation ($input: CredentialsFromFederatedCredentialInput!) {
            auth {
                credentialsFromFederatedCredential(input: $input) {
                    __typename
                    ... on UserCredentials {
                        user { id displayName email emailVerified avatarUrl }
                        accessToken
                        refreshToken
                        expiresIn
                    }
                }
            }
        }
        """,
        variable_values={
            "input": {"credential": oidc_token, "provider": federated_identity_provider_name}
        },
        context_value=context,
    )
    assert result.errors is None
    assert result.data is not None

    creds = result.data["auth"]["credentialsFromFederatedCredential"]
    assert_credentials_for_user(creds, federated_credential_user)


@pytest.mark.asyncio
async def test_basic_sign_up(
    db_session: AsyncSession,
    federated_identity_provider_name: str,
    oidc_token: str,
    context,
):
    result = await schema.execute(
        """
        mutation ($input: CredentialsFromFederatedCredentialInput!) {
            auth {
                credentialsFromFederatedCredential(input: $input) {
                    __typename
                    ... on UserCredentials {
                        user { id displayName email emailVerified avatarUrl }
                        accessToken
                        refreshToken
                        expiresIn
                    }
                }
            }
        }
        """,
        variable_values={
            "input": {
                "credential": oidc_token,
                "provider": federated_identity_provider_name,
                "isNewUser": True,
            }
        },
        context_value=context,
    )
    assert result.errors is None
    assert result.data is not None

    creds = result.data["auth"]["credentialsFromFederatedCredential"]
    user = (
        await db_session.execute(sa.select(dbm.User).where(dbm.User.uuid == creds["user"]["id"]))
    ).scalar_one()
    assert_credentials_for_user(creds, user)


@pytest.mark.asyncio
async def test_bad_provider(
    faker: Faker,
    oidc_token: str,
    context,
):
    result = await schema.execute(
        """
        mutation ($input: CredentialsFromFederatedCredentialInput!) {
            auth {
                credentialsFromFederatedCredential(input: $input) {
                    __typename
                    ... on AuthError { error }
                }
            }
        }
        """,
        variable_values={"input": {"credential": oidc_token, "provider": faker.slug()}},
        context_value=context,
    )
    assert result.errors is None
    assert result.data is not None

    error = result.data["auth"]["credentialsFromFederatedCredential"]
    assert error["error"] == "NO_SUCH_FEDERATED_IDENTITY_PROVIDER"


@pytest.mark.asyncio
async def test_bad_credential(
    faker: Faker,
    federated_identity_provider_name: str,
    context,
):
    result = await schema.execute(
        """
        mutation ($input: CredentialsFromFederatedCredentialInput!) {
            auth {
                credentialsFromFederatedCredential(input: $input) {
                    __typename
                    ... on AuthError { error }
                }
            }
        }
        """,
        variable_values={
            "input": {"credential": "bad-credential", "provider": federated_identity_provider_name}
        },
        context_value=context,
    )
    assert result.errors is None
    assert result.data is not None

    error = result.data["auth"]["credentialsFromFederatedCredential"]
    assert error["error"] == "INVALID_FEDERATED_CREDENTIAL"


@pytest.mark.asyncio
async def test_sign_up_existing_user(
    federated_identity_provider_name: str,
    oidc_token: str,
    federated_credential_user: dbm.User,
    context,
):
    result = await schema.execute(
        """
        mutation ($input: CredentialsFromFederatedCredentialInput!) {
            auth {
                credentialsFromFederatedCredential(input: $input) {
                    __typename
                    ... on AuthError {
                        error
                    }
                }
            }
        }
        """,
        variable_values={
            "input": {
                "credential": oidc_token,
                "provider": federated_identity_provider_name,
                "isNewUser": True,
            }
        },
        context_value=context,
    )
    assert result.errors is None
    assert result.data is not None

    error = result.data["auth"]["credentialsFromFederatedCredential"]
    assert error["error"] == "USER_ALREADY_SIGNED_UP"


@pytest.mark.asyncio
async def test_basic_refresh(
    faker: Faker,
    users: list[dbm.User],
    authentication_provider: auth.AuthenticationProvider,
    context,
):
    user = faker.random_element(users)
    credentials = await authentication_provider.create_user_credentials(user)

    result = await schema.execute(
        """
        mutation ($input: RefreshCredentialsInput!) {
            auth {
                refreshCredentials(input: $input) {
                    __typename
                    ... on UserCredentials {
                        user { id displayName email emailVerified avatarUrl }
                        accessToken
                        refreshToken
                        expiresIn
                    }
                }
            }
        }
        """,
        variable_values={"input": {"refreshToken": credentials.refresh_token}},
        context_value=context,
    )
    assert result.errors is None
    assert result.data is not None

    creds = result.data["auth"]["refreshCredentials"]
    assert_credentials_for_user(creds, user)


@pytest.mark.asyncio
async def test_refresh_bad_token(
    faker: Faker,
    users: list[dbm.User],
    authentication_provider: auth.AuthenticationProvider,
    context,
):
    result = await schema.execute(
        """
        mutation ($input: RefreshCredentialsInput!) {
            auth {
                refreshCredentials(input: $input) {
                    __typename
                    ... on AuthError {
                        error
                    }
                }
            }
        }
        """,
        variable_values={"input": {"refreshToken": faker.slug()}},
        context_value=context,
    )
    assert result.errors is None
    assert result.data is not None

    error = result.data["auth"]["refreshCredentials"]
    assert error["error"] == "INVALID_CREDENTIAL"
