"""
pytest configuration and fixtures

"""
import pytest

from faker import Faker
from flask import Flask
from mixer.backend.flask import Mixer

from componentsdb.model import db as _db, Component

@pytest.fixture(scope='module')
def app():
    app = Flask(__name__)
    app.debug = True
    app.config['TESTING'] = True
    return app

@pytest.fixture(scope='module')
def db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///comp_testing'
    app.config['SQLALCHEMY_ECHO'] = True
    _db.init_app(app)
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
