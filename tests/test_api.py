"""
Test JSON API.

"""
# pylint: disable=redefined-outer-name

from flask import url_for

def test_profile_needs_auth(client):
    """Authorisation is needed to get profile."""
    assert client.get(url_for('api.profile')).status_code == 401

def test_profile_allows_auth(client, user_api_headers):
    """Authorisation is suffient to get profile."""
    r = client.get(url_for('api.profile'), headers=user_api_headers)
    assert r.status_code == 200

def test_profile_needs_bearer_auth(client):
    """Anything other than bearer auth is a bad request."""
    assert client.get(
        url_for('api.profile'), headers={'Authorization': 'Basic foobar'}
    ).status_code == 400
    assert client.get(
        url_for('api.profile'), headers={'Authorization': 'Some other scheme'}
    ).status_code == 400

def test_profile_matches_user(user, client, user_api_headers):
    """Profile matches the authorised user."""
    r = client.get(url_for('api.profile'), headers=user_api_headers).json
    assert 'name' in r
    assert r['name'] == user.name
