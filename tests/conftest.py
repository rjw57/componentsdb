"""
pytest configuration and fixtures

"""
import pytest

from faker import Faker
from mixer.backend.flask import Mixer

from componentsdb.app import create_app
from componentsdb.model import (
    db as _db, Component, User, UserComponentPermission
)

@pytest.fixture(scope='module')
def app():
    _app = create_app()
    _app.debug = True
    _app.config['TESTING'] = True
    return _app

@pytest.fixture(scope='module')
def db(app):
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///comp_testing'
    _db.init_app(app)
    return _db

@pytest.fixture(scope='module')
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

@pytest.fixture(scope='module')
def user(mixer):
    """A fake test user."""
    return mixer.blend(User)
