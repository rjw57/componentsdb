import pytest
from faker import Faker
from fastapi.testclient import TestClient

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
        return init_settings


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
def client():
    return TestClient(app)
