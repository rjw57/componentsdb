# pylint: disable=redefined-outer-name

import datetime
import logging

import jwt
import pytest
import mock

from componentsdb.auth import (
    verify_google_id_token, _get_default_certs, user_for_google_id_token
)
from componentsdb.model import UserIdentity
from oauth2client.crypt import AppIdentityError
from werkzeug.exceptions import BadRequest, HTTPException

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
def google_token(app, valid_payload):
    return _encode_valid_token(app, valid_payload)

def test_google_get_default_certs(app):
    """Get default certs should fetch the Google certificates."""
    # pylint: disable=unused-argument
    assert len(_get_default_certs()) > 0

def test_google_get_default_certs_checks_status(app):
    """Get default certs should fetch the Google certificates but also check the
    status code of the response.."""
    # pylint: disable=unused-argument
    mock_resp = mock.MagicMock()
    mock_resp.status_code.return_value = 500
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

def test_google_user_creation(google_token, valid_payload):
    # pylint: disable=no-member

    # Check user does not exist with this identity
    assert UserIdentity.query.filter(
        UserIdentity.provider == 'google',
        UserIdentity.provider_identity == valid_payload['sub']
    ).first() is None

    # Check creation of user
    u = user_for_google_id_token(google_token)
    assert u is not None
    assert u.name == valid_payload['email']
    assert u.id is not None # => it is in the database

    # Check identity is added
    assert UserIdentity.query.filter(
        UserIdentity.provider == 'google',
        UserIdentity.provider_identity == valid_payload['sub']
    ).count() == 1

def test_google_user_retrieval(google_token, valid_payload):
    # pylint: disable=no-member

    # Check user does not exist with this identity
    assert UserIdentity.query.filter(
        UserIdentity.provider == 'google',
        UserIdentity.provider_identity == valid_payload['sub']
    ).first() is None

    # Create user
    u = user_for_google_id_token(google_token)
    assert u is not None
    assert u.id is not None

    # Retrieve user. It should be the same one.
    u2 = user_for_google_id_token(google_token)
    assert u2 is not None
    assert u2.id == u.id

    # Check identity is added only once
    assert UserIdentity.query.filter(
        UserIdentity.provider == 'google',
        UserIdentity.provider_identity == valid_payload['sub']
    ).count() == 1
