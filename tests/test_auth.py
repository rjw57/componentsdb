# pylint: disable=redefined-outer-name

import datetime
import logging

import jwt
import pytest
import mock
from flask import json
from oauth2client.crypt import AppIdentityError
from werkzeug.exceptions import BadRequest, HTTPException

from componentsdb.auth import (
    verify_google_id_token, _get_default_certs, user_for_google_id_token,
    associate_user_with_google_id
)
from componentsdb.model import UserIdentity

def _encode_valid_token(app, payload):
    logging.info('encoding token payload: %s', payload)
    key = list(app.config.get('TESTING_GOOGLE_OAUTH2_CERT_PRIV_KEYS').values())[0]
    t = jwt.encode(payload, key, algorithm='RS256').decode('ascii')
    logging.info('encoded token: %s', t)
    return t

def _encode_invalid_token(payload):
    logging.info('encoding token payload: %s', payload)
    key = 'somesecret'
    t = jwt.encode(payload, key).decode('ascii')
    logging.info('encoded token: %s', t)
    return t

@pytest.fixture
def valid_payload(app, fake):
    client_id = app.config['GOOGLE_OAUTH2_ALLOWED_CLIENT_IDS'][0]
    return dict(
        iat=datetime.datetime.utcnow() - datetime.timedelta(minutes=1),
        exp=datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        aud=client_id, iss='accounts.google.com',
        sub=fake.numerify('################################'),
        email=fake.safe_email(), email_verified=False,
    )

@pytest.fixture
def no_user_google_token(app, valid_payload):
    # pylint: disable=no-member
    assert UserIdentity.query.filter(
        UserIdentity.provider == 'google',
        UserIdentity.provider_identity == valid_payload['sub']
    ).first() is None
    return _encode_valid_token(app, valid_payload)

def test_google_get_default_certs(app):
    """Get default certs should fetch the Google certificates."""
    # pylint: disable=unused-argument
    mock_resp = mock.MagicMock()
    mock_resp.status = 200
    content = json.dumps(dict(foo='bar', buzz='quux'))
    p = mock.patch(
        'componentsdb.auth._cached_http.request',
        return_value=(mock_resp, content)
    )
    with p as o:
        cs = _get_default_certs()
        o.assert_called_with('https://www.googleapis.com/oauth2/v1/certs')

    assert cs == json.loads(content)

def test_google_get_default_certs_checks_status(app):
    """Get default certs should fetch the Google certificates but also check the
    status code of the response.."""
    # pylint: disable=unused-argument
    mock_resp = mock.MagicMock()
    mock_resp.status = 500
    p = mock.patch(
        'componentsdb.auth._cached_http.request',
        return_value=(mock_resp, '')
    )
    with p, pytest.raises(HTTPException):
        _get_default_certs()

def test_google_basic_verify(app, valid_payload):
    t = _encode_valid_token(app, valid_payload)
    idinfo = verify_google_id_token(t)
    logging.info('Verfied payload: %s', idinfo)

def test_google_verifies_signature(valid_payload):
    t = _encode_invalid_token(valid_payload)
    with pytest.raises(AppIdentityError):
        verify_google_id_token(t)

def test_google_iss(app, valid_payload):
    """iss must be accounts.google.com or https://accounts.google.com"""
    valid_payload['iss'] = 'accounts.google.com'
    t = _encode_valid_token(app, valid_payload)
    idinfo = verify_google_id_token(t)
    logging.info('Verfied payload: %s', idinfo)

    valid_payload['iss'] = 'https://accounts.google.com'
    t = _encode_valid_token(app, valid_payload)
    idinfo = verify_google_id_token(t)
    logging.info('Verfied payload: %s', idinfo)

def test_google_needs_iss(app, valid_payload):
    del valid_payload['iss']
    t = _encode_valid_token(app, valid_payload)
    with pytest.raises(AppIdentityError):
        verify_google_id_token(t)

def test_google_needs_valid_iss(app, valid_payload):
    valid_payload['iss'] = 'some.attacker.example.com'
    t = _encode_valid_token(app, valid_payload)
    with pytest.raises(AppIdentityError):
        verify_google_id_token(t)

def test_google_needs_aud(app, valid_payload):
    del valid_payload['aud']
    t = _encode_valid_token(app, valid_payload)
    with pytest.raises(AppIdentityError):
        verify_google_id_token(t)

def test_google_needs_matching_aud(app, valid_payload):
    valid_payload['aud'] += '.but.a.wrong.one'
    t = _encode_valid_token(app, valid_payload)
    with pytest.raises(AppIdentityError):
        verify_google_id_token(t)

def test_google_needs_iat(app, valid_payload):
    del valid_payload['iat']
    t = _encode_valid_token(app, valid_payload)
    with pytest.raises(AppIdentityError):
        verify_google_id_token(t)

def test_google_needs_valid_iat(app, valid_payload):
    valid_payload['iat'] = datetime.datetime.utcnow() + datetime.timedelta(days=200)
    t = _encode_valid_token(app, valid_payload)
    with pytest.raises(AppIdentityError):
        verify_google_id_token(t)

def test_google_needs_exp(app, valid_payload):
    del valid_payload['exp']
    t = _encode_valid_token(app, valid_payload)
    with pytest.raises(AppIdentityError):
        verify_google_id_token(t)

def test_google_needs_valid_exp(app, valid_payload):
    valid_payload['exp'] = datetime.datetime.utcnow() - datetime.timedelta(days=200)
    t = _encode_valid_token(app, valid_payload)
    with pytest.raises(AppIdentityError):
        verify_google_id_token(t)

def test_google_user_needs_sub(app, valid_payload):
    del valid_payload['sub']
    t = _encode_valid_token(app, valid_payload)
    with pytest.raises(BadRequest):
        user_for_google_id_token(t)

def test_google_user_needs_valid_token(app, valid_payload):
    # pylint: disable=unused-argument
    t = _encode_invalid_token(valid_payload)
    with pytest.raises(BadRequest):
        user_for_google_id_token(t)

def test_google_user_needs_email(app, valid_payload):
    del valid_payload['email']
    t = _encode_valid_token(app, valid_payload)
    with pytest.raises(BadRequest):
        user_for_google_id_token(t)

def test_google_user_creation(no_user_google_token, valid_payload):
    # pylint: disable=no-member

    # Check creation of user
    u = user_for_google_id_token(no_user_google_token)
    assert u is not None
    assert u.name == valid_payload['email']
    assert u.id is not None # => it is in the database

    # Check identity is added
    assert UserIdentity.query.filter(
        UserIdentity.provider == 'google',
        UserIdentity.provider_identity == valid_payload['sub']
    ).count() == 1

def test_google_user_retrieval(no_user_google_token, valid_payload):
    # pylint: disable=no-member

    # Create user
    u = user_for_google_id_token(no_user_google_token)
    assert u is not None
    assert u.id is not None

    # Retrieve user. It should be the same one.
    u2 = user_for_google_id_token(no_user_google_token)
    assert u2 is not None
    assert u2.id == u.id

    # Check identity is added only once
    assert UserIdentity.query.filter(
        UserIdentity.provider == 'google',
        UserIdentity.provider_identity == valid_payload['sub']
    ).count() == 1

def test_google_user_association(no_user_google_token, user):
    associate_user_with_google_id(user, no_user_google_token)
    u = user_for_google_id_token(no_user_google_token)
    assert u.id == user.id

def test_google_user_association_requires_sub(app, user, valid_payload):
    del valid_payload['sub']
    t = _encode_valid_token(app, valid_payload)
    with pytest.raises(BadRequest):
        associate_user_with_google_id(user, t)

def test_google_user_association_requires_valid_token(user, valid_payload):
    t = _encode_invalid_token(valid_payload)
    with pytest.raises(BadRequest):
        associate_user_with_google_id(user, t)

def test_google_user_multiple_association(db, valid_payload, no_user_google_token, user):
    """Repeatedly associating an id only affects one row."""
    # pylint: disable=no-member

    for _ in range(10):
        associate_user_with_google_id(user, no_user_google_token)
        db.session.commit()

    u = user_for_google_id_token(no_user_google_token)
    assert u.id == user.id

    # Check identity is added only once
    assert UserIdentity.query.filter(
        UserIdentity.provider == 'google',
        UserIdentity.provider_identity == valid_payload['sub']
    ).count() == 1

def test_google_user_fixture(google_id_token, user):
    """Test that retrieving the user associated with the google_token fixture
    gives the correct user."""
    u = user_for_google_id_token(google_id_token)
    assert u.id == user.id

