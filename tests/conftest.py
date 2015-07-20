"""
pytest configuration and fixtures

"""
import pytest

from faker import Faker
from mixer.backend.flask import Mixer

from componentsdb.app import app as _app
from componentsdb.model import db as _db, Component

@pytest.fixture(scope='module')
def app():
    _app.debug = True
    _app.config['TESTING'] = True
    return _app

@pytest.fixture(scope='module')
def db(app):
    app.config['SQLALCHEMY_ECHO'] = True
    return _db

@pytest.fixture(scope='module')
def mixer(app, db):
    faker = Faker()

    mixer = Mixer(commit=True)
    mixer.init_app(app)

    mixer.register(
        Component, code=faker.slug, description=faker.sentence,
        datasheet_url=faker.uri,
    )

    return mixer
