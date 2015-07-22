"""
pytest configuration and fixtures

"""
# pylint: disable=redefined-outer-name

import pytest

# pylint: disable=import-error
from faker import Faker
from mixer.backend.flask import Mixer

from componentsdb.app import (
    default_app, set_current_user_with_token, current_user as _current_user
)
from componentsdb.model import (
    Component, Collection, User, UserCollectionPermission, Permission,
    UserIdentity, db as _db,
)

_app = default_app()

@pytest.fixture(scope='session')
def app():
    return _app

@pytest.fixture(scope='session')
def db():
    return _db

@pytest.fixture(scope='session')
def mixer(app):
    faker = Faker()

    mixer = Mixer(commit=True)
    mixer.init_app(app)

    mixer.register(
        Component, code=faker.slug, description=faker.sentence,
        datasheet_url=faker.uri
    )

    mixer.register(User, name=faker.name)
    mixer.register(Collection, name=faker.text)
    mixer.register(
        UserCollectionPermission, permission=faker.random_element(Permission)
    )

    return mixer

@pytest.fixture
def user(mixer):
    """A fake test user."""
    return mixer.blend(User)

@pytest.fixture
def current_user(user):
    """The fake user "user" authenticated as the current user."""
    set_current_user_with_token(user.token)
    return _current_user

@pytest.fixture
def user_api_headers(user):
    """Authorisation headers for a client acting as the fixture user."""
    t = user.token
    return {'Authorization': 'Bearer %s' % t.decode('ascii')}

@pytest.fixture
def component(mixer):
    """A newly inserted component with random values."""
    c = mixer.blend(
        Component, code=mixer.FAKE, description=mixer.FAKE,
        datasheet_url=mixer.FAKE,
    )
    return c

@pytest.fixture
def collection(mixer):
    """A newly inserted collection with random values."""
    c = mixer.blend(Collection, name=mixer.FAKE)
    return c

@pytest.fixture
def user_collection_permission(mixer, user, collection):
    """A newly inserted collection with random values."""
    c = mixer.blend(UserCollectionPermission, user=user, collection=collection)
    return c

@pytest.fixture
def user_identity(mixer, user):
    """A newly inserted identity with random values."""
    c = mixer.blend(UserIdentity, user=user)
    return c
