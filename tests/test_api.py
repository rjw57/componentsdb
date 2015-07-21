"""
Test JSON API.

"""
# pylint: disable=redefined-outer-name
from __future__ import division

import logging
import math
import random

import pytest
from flask import url_for, json

from componentsdb.model import Permission, Collection

def _post_json(client, url, data, headers=None):
    """Post JSON encoded data to url via client optionally setting headers."""
    h = {'Content-Type': 'application/json'}
    h.update(headers)
    return client.post(url, data=json.dumps(data), headers=h)

def _put_json(client, url, data, headers=None):
    """Put JSON encoded data to url via client optionally setting headers."""
    h = {'Content-Type': 'application/json'}
    h.update(headers)
    return client.put(url, data=json.dumps(data), headers=h)

@pytest.fixture(params=[0, 1e-20, 0.9, 1.1, 1, 2, 2.2, 5])
def many_collections(mixer, user, app, request):
    """Create a number of collections numbering around the page size for the
    fixture user."""
    n_collections = int(math.ceil(request.param * app.config['PAGE_SIZE']))
    assert n_collections >= 0
    logging.info('Creating %s collection(s) for user', n_collections)

    cs = mixer.cycle(n_collections).blend(Collection, name=mixer.FAKE)
    for c in cs:
        c.add_all_permissions(user)

    return cs

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

def test_collection_create_needs_auth(client):
    """Authorisation is needed to create a collection."""
    assert client.put(url_for('api.collections')).status_code == 401

def test_collection_create_succeeds(client, user_api_headers):
    """Creating a collection should succeed."""
    request = dict(name='foobar-%s' % random.random())
    r = _put_json(
        client, url_for('api.collections'), request, user_api_headers
    )
    assert r.status_code == 201 # created

def test_collection_create_needs_json(client, user_api_headers):
    """Creating a collection should succeed."""
    request = dict(name='foobar-%s' % random.random())
    r = client.put(
        url_for('api.collections'), data=request, headers=user_api_headers
    )
    assert r.status_code == 400 # bad request

def test_collection_create_returns_url(client, user_api_headers):
    """Creating a collection should return a URL to the resource."""
    # pylint: disable=no-member

    request = dict(name='foobar-%s' % random.random())
    r = _put_json(
        client, url_for('api.collections'), request, user_api_headers
    )
    assert r.status_code == 201 # created

    data = r.json
    logging.info('response: %s', data)

    assert 'url' in data

    # check URL can be "GET"-ed to retrieve collection
    r = client.get(data['url'], headers=user_api_headers)
    assert r.status_code == 200
    data = r.json
    logging.info('collection response: %s', data)

    # check name matches
    assert 'name' in data
    assert data['name'] == request['name']

def test_collection_get_needs_read(client, current_user, user_api_headers, collection):
    # make sure no read permission
    assert not collection.has_permission(current_user, Permission.READ)

    # get URL
    r = client.get(
        url_for('api.collection', key=collection.encoded_key),
        headers=user_api_headers,
    )
    assert r.status_code == 404

def test_collection_get_allows_read(client, current_user, user_api_headers, collection):
    # make sure no read permission
    assert not collection.has_permission(current_user, Permission.READ)

    # add read permission
    collection.add_permission(current_user, Permission.READ)

    # get URL
    r = client.get(
        url_for('api.collection', key=collection.encoded_key),
        headers=user_api_headers,
    )
    assert r.status_code == 200

def test_collection_get_matched(client, current_user, user_api_headers, collection):
    # add read permission
    collection.add_permission(current_user, Permission.READ)

    # get URL
    r = client.get(
        url_for('api.collection', key=collection.encoded_key),
        headers=user_api_headers,
    )
    assert r.status_code == 200

    data = r.json
    assert data is not None

    assert data['name'] == collection.name

def test_collection_list_needs_auth(client):
    """Authorisation is needed to list a collection."""
    assert client.get(url_for('api.collections')).status_code == 401

def test_collection_list_succeeds(client, user_api_headers):
    r = client.get(
        url_for('api.collections'), headers=user_api_headers
    )
    assert r.status_code == 200

def test_collection_list_pagination(
        many_collections, app, client, user_api_headers):
    cs = many_collections
    expected_pages = int(math.ceil(len(cs) / app.config['PAGE_SIZE']))

    # Get all pages from resource
    logging.info('Expected page count: %s', expected_pages)

    n_pages = 0
    url = url_for('api.collections')
    while True:
        r = client.get(url, headers=user_api_headers)
        assert r.status_code == 200
        data = r.json

        # Break out when empty page reached
        if len(data['resources']) == 0 or n_pages > expected_pages:
            break

        # Follow next URL
        url = data['next']

        # Increment page count
        n_pages += 1

    assert n_pages == expected_pages
