import gql
import pytest
import pytest_asyncio
from faker import Faker
from gql.transport.httpx import HTTPXAsyncTransport
from httpx import ASGITransport, AsyncClient

from componentsdb.auth import AuthenticationProvider
from componentsdb.db import models as dbm
from componentsdb.fastapi import app
from componentsdb.fastapi.db import get_db_session
from componentsdb.fastapi.settings import Settings, load_settings


class TestSettings(Settings):
    # Only load values explicitly passed to __init__().
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (init_settings,)


@pytest.fixture(autouse=True)
def override_dependencies(faker: Faker, db_session, federated_identity_providers):
    async def _get_db_session():
        yield db_session
        await db_session.flush()

    def _load_settings():
        return TestSettings(
            sqlalchemy_db_url=faker.url(schemes=["postgresql+asyncpg"]),
            federated_identity_providers=federated_identity_providers,
        )

    app.dependency_overrides[get_db_session] = _get_db_session
    app.dependency_overrides[load_settings] = _load_settings


@pytest.fixture
def httpx_client_kwargs():
    return {"transport": ASGITransport(app=app), "base_url": "https://test.invalid"}


@pytest.fixture
def authenticated_user(faker: Faker, users: list[dbm.User]):
    return faker.random_element(users)


@pytest_asyncio.fixture
async def access_token(
    authenticated_user: dbm.User, authentication_provider: AuthenticationProvider
):
    credentials = await authentication_provider.create_user_credentials(authenticated_user)
    return credentials.access_token


@pytest_asyncio.fixture
async def unauthenticated_client(httpx_client_kwargs):
    async with AsyncClient(**httpx_client_kwargs) as client:
        yield client


@pytest_asyncio.fixture
async def client(httpx_client_kwargs, access_token):
    async with AsyncClient(
        headers={"Authorization": f"Bearer {access_token}"}, **httpx_client_kwargs
    ) as client:
        yield client


@pytest.fixture
def make_gql_client(httpx_client_kwargs):
    def _make_gql_client(*, transport_kwargs=None):
        transport = HTTPXAsyncTransport(
            "/graphql",
            **httpx_client_kwargs,
            **(transport_kwargs if transport_kwargs is not None else dict()),
        )

        return gql.Client(transport=transport, fetch_schema_from_transport=True)

    return _make_gql_client


@pytest_asyncio.fixture
async def unauthenticated_gql_session(make_gql_client):
    async with make_gql_client() as session:
        yield session


@pytest_asyncio.fixture
async def gql_session(make_gql_client, access_token):
    async with make_gql_client(
        transport_kwargs={
            "headers": {"Authorization": f"Bearer {access_token}"},
        },
    ) as session:
        yield session
