import pytest
from faker import Faker
from gql import gql
from gql.client import AsyncClientSession
from gql.transport.exceptions import TransportServerError


@pytest.mark.asyncio
async def test_unauthenticated_user(unauthenticated_gql_session: AsyncClientSession):
    result = await unauthenticated_gql_session.execute(
        gql("query { auth { authenticatedUser { id } } }")
    )
    assert result["auth"]["authenticatedUser"] is None


@pytest.mark.asyncio
async def test_authenticated(gql_session: AsyncClientSession, authenticated_user):
    result = await gql_session.execute(gql("query { auth { authenticatedUser { id } } }"))
    assert result["auth"]["authenticatedUser"]["id"] == str(authenticated_user.uuid)


@pytest.mark.asyncio
@pytest.mark.parametrize("scheme", ["Not-Bearer", "Bearer"])
async def test_bad_auth(scheme: str, faker: Faker, make_gql_client, authenticated_user):
    with pytest.raises(TransportServerError) as excinfo:
        async with make_gql_client(
            transport_kwargs={
                "headers": {"Authorization": f"{scheme} {faker.uuid4()}"},
            },
        ) as session:
            await session.execute(gql("query { auth { authenticatedUser { id } } }"))
    assert excinfo.value.code == 403
