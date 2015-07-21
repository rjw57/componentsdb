"""
pytest configuration and fixtures

"""
import pytest

from faker import Faker
from mixer.backend.flask import Mixer

from componentsdb.app import default_app, db as _db
from componentsdb.model import (
    Component, User, UserComponentPermission
)

_app = default_app()

@pytest.fixture(scope='session')
def app():
    return _app

@pytest.fixture(scope='session')
def db(app):
    return _db

@pytest.fixture(scope='session')
def mixer(app, db):
    faker = Faker()

    mixer = Mixer(commit=True)
    mixer.init_app(app)

    mixer.register(
        Component, code=faker.slug, description=faker.sentence,
        datasheet_url=faker.uri
    )

    mixer.register(User, name=faker.name)

    return mixer

@pytest.fixture(scope='session')
def user(mixer):
    """A fake test user."""
    return mixer.blend(User)
