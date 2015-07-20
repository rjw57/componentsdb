"""
pytest configuration and fixtures

"""
import pytest

from faker import Faker
from mixer.backend.flask import Mixer

from componentsdb.app import create_app, db as _db
from componentsdb.model import (
    Component, User, UserComponentPermission
)

def _create_app():
    app = create_app()

    app.debug = True
    app.secret_key = 'hello, world'
    app.testing = True

    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///comp_testing'
    return app

_app = _create_app()
_db.init_app(_app)

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
