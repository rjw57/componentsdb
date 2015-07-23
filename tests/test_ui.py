# pylint: disable=redefined-outer-name

import logging

import pytest
from flask import url_for, session

from componentsdb.app import current_user
from componentsdb.model import User, Collection
from componentsdb.ui import AUTH_TOKEN_SESSION_KEY

# Python 3/2 compatibility
try:
    # pylint: disable=no-name-in-module,import-error
    from urllib.parse import urlparse
except ImportError:
    # pylint: disable=no-name-in-module,import-error
    from urlparse import urlparse

@pytest.fixture
def auth_client(client, google_id_token):
    """A client signed in as the user fixture."""
    client.get(url_for('ui.signin_with_google_token', token=google_id_token))
    return client

def assert_path_equals(url, path):
    assert urlparse(url).path == path

def assert_redirect_to_sign_in(r):
    assert r.status_code == 302
    assert_path_equals(r.headers['Location'], url_for('ui.signin'))

def test_unauth_client_redirects_signin(client):
    r = client.get(url_for('ui.index'))
    assert_redirect_to_sign_in(r)
    logging.info(
        'unauthorised get of ui.index redirects to: %s', r.headers['Location']
    )
    r = client.get(r.headers['Location'])
    assert r.status_code == 200

def test_exchange_google_id(google_id_token, user, client):
    # not currently signed in
    assert session.get('componentsdb_auth') is None

    r = client.get(url_for('ui.signin_with_google_token', token=google_id_token))
    assert r.status_code == 302 # should re-direct
    assert_path_equals(r.headers['Location'], url_for('ui.index'))

    token = session.get(AUTH_TOKEN_SESSION_KEY)
    assert token is not None

    assert User.decode_token(token) == user.id

def test_exchange_google_id_needs_token(client):
    r = client.get(url_for('ui.signin_with_google_token'))
    assert r.status_code == 400 # bad request

def test_exchange_google_id_redirects(client, google_id_token):
    r = client.get(url_for(
        'ui.signin_with_google_token', token=google_id_token, target='/foo/bar'
    ))
    assert r.status_code == 302
    assert_path_equals(r.headers['Location'], '/foo/bar')

def test_exchange_google_id_needs_valid_token(client):
    r = client.get(url_for('ui.signin_with_google_token', token='not-a-token'))
    assert r.status_code == 400

def test_index(auth_client):
    r = auth_client.get(url_for('ui.index'))
    assert r.status_code == 200

def test_signin_when_signed_in(auth_client):
    r = auth_client.get(url_for('ui.signin'))
    assert r.status_code == 302
    assert_path_equals(r.headers['Location'], url_for('ui.index'))

def test_signin_with_token(client, user):
    r = client.get(url_for('ui.signin', token=user.token))
    assert r.status_code == 302
    assert_path_equals(r.headers['Location'], url_for('ui.index'))
    r = client.get(r.headers['Location'])
    assert current_user.id == user.id

def test_signout(auth_client):
    r = auth_client.get(url_for('ui.signout'))
    assert r.status_code == 302
    assert_path_equals(r.headers['Location'], url_for('ui.index'))
    assert session.get(AUTH_TOKEN_SESSION_KEY) is None

def test_collection_without_read_is_404(auth_client, mixer):
    c = mixer.blend(Collection)
    r = auth_client.get(url_for('ui.collection', key=c.encoded_key))
    assert r.status_code == 404

def test_collection_with_read_succeeds(auth_client, user, mixer):
    c = mixer.blend(Collection)
    c.add_all_permissions(user)
    r = auth_client.get(url_for('ui.collection', key=c.encoded_key))
    assert r.status_code == 200

def test_create_collection_needs_auth(client):
    r = client.get(url_for('ui.collection_create'))
    assert_redirect_to_sign_in(r)

def test_create_collection_get(auth_client):
    r = auth_client.get(url_for('ui.collection_create'))
    assert r.status_code == 200

def test_create_collection_post(auth_client, fake):
    # pylint: disable=no-member

    name = fake.text()
    data = dict(name=name)
    r = auth_client.post(url_for('ui.collection_create'), data=data)
    assert r.status_code == 302 # redirects

    # redirect exists
    r = auth_client.get(r.headers['Location'])
    assert r.status_code == 200

    # collection actually created
    assert Collection.query.filter(name == name).first() is not None

def test_create_collection_post_needs_name(auth_client, fake):
    r = auth_client.post(url_for('ui.collection_create'))
    assert r.status_code >= 400 # bad
