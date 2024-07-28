import pytest

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
