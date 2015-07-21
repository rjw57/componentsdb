"""
Test JSON API.

"""
import json

import pytest
from flask import url_for

@pytest.fixture
def auth_headers(app, user):
    """Create a client authorised as the user fixture."""
    t = user.token
    return { 'Authorization': 'Bearer %s' % t.decode('ascii') }

def test_profile_needs_auth(client):
    """Authorisation is needed to get profile."""
    assert client.get(url_for('api.profile')).status_code == 401

def test_profile_allows_auth(client, auth_headers):
    """Authorisation is suffient to get profile."""
    r = client.get(url_for('api.profile'), headers=auth_headers)
    assert r.status_code == 200

def test_profile_matches_user(user, client, auth_headers):
    """Profile matches the authorised user."""
    r = client.get(url_for('api.profile'), headers=auth_headers).json
    assert 'name' in r
    assert r['name'] == user.name
