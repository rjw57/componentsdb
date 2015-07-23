"""
pytest configuration and fixtures

"""
# pylint: disable=redefined-outer-name
import datetime

import jwt
import pytest

# pylint: disable=import-error
from faker import Faker
from mixer.backend.flask import Mixer

from componentsdb.app import (
    default_app, set_current_user_with_token, current_user as _current_user
)
from componentsdb.auth import associate_user_with_google_id
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
def fake():
    return Faker()

@pytest.fixture(scope='session')
def mixer(app, fake):
    mixer = Mixer(commit=True)
    mixer.init_app(app)

    mixer.register(
        Component, code=fake.slug, description=fake.sentence,
        datasheet_url=fake.uri
    )

    mixer.register(User, name=fake.name)
    mixer.register(Collection, name=fake.text)
    mixer.register(
        UserCollectionPermission, permission=fake.random_element(Permission)
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

@pytest.fixture
def google_id_token(app, user, fake):
    """A google id token for an identity associated with the user fixture."""
    client_id = app.config['GOOGLE_OAUTH2_ALLOWED_CLIENT_IDS'][0]
    payload = dict(
        iat=datetime.datetime.utcnow() - datetime.timedelta(minutes=1),
        exp=datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        aud=client_id, iss='accounts.google.com',
        sub=fake.numerify('################################'),
        email=fake.safe_email(), email_verified=False,
    )
    key = list(app.config.get('TESTING_GOOGLE_OAUTH2_CERT_PRIV_KEYS').values())[0]
    t = jwt.encode(payload, key, algorithm='RS256').decode('ascii')
    associate_user_with_google_id(user, t)
    return t
