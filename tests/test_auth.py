import datetime
import logging

import jwt
import pytest

from componentsdb.auth import verify_google_id_token, _get_default_certs
from oauth2client.crypt import AppIdentityError

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

def _valid_payload(client_id):
    return dict(
        iat=datetime.datetime.utcnow() - datetime.timedelta(minutes=1),
        exp=datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        aud=client_id, iss='accounts.google.com',
    )

def test_google_get_default_certs(app):
    """Get default certs should fetch the Google certificates."""
    # pylint: disable=unused-argument
    assert len(_get_default_certs()) > 0

def test_google_basic_verify(app):
    client_id = 'i.am.a.client'
    p = _valid_payload(client_id)
    t = _encode_valid_token(app, p)
    idinfo = verify_google_id_token(t, client_id)
    logging.info('Verfied payload: %s', idinfo)

def test_google_verifies_signature(app):
    # pylint: disable=unused-argument
    client_id = 'i.am.a.client'
    p = _valid_payload(client_id)
    t = _encode_invalid_token(p)
    with pytest.raises(AppIdentityError):
        verify_google_id_token(t, client_id)

def test_google_iss(app):
    """iss must be accounts.google.com or https://accounts.google.com"""
    client_id = 'i.am.a.client'
    p = _valid_payload(client_id)

    p['iss'] = 'accounts.google.com'
    t = _encode_valid_token(app, p)
    idinfo = verify_google_id_token(t, client_id)
    logging.info('Verfied payload: %s', idinfo)

    p['iss'] = 'https://accounts.google.com'
    t = _encode_valid_token(app, p)
    idinfo = verify_google_id_token(t, client_id)
    logging.info('Verfied payload: %s', idinfo)

def test_google_needs_iss(app):
    client_id = 'i.am.a.client'
    p = _valid_payload(client_id)
    del p['iss']
    t = _encode_valid_token(app, p)
    with pytest.raises(AppIdentityError):
        verify_google_id_token(t, client_id)

def test_google_needs_valid_iss(app):
    client_id = 'i.am.a.client'
    p = _valid_payload(client_id)
    p['iss'] = 'some.attacker.example.com'
    t = _encode_valid_token(app, p)
    with pytest.raises(AppIdentityError):
        verify_google_id_token(t, client_id)

def test_google_needs_aud(app):
    client_id = 'i.am.a.client'
    p = _valid_payload(client_id)
    del p['aud']
    t = _encode_valid_token(app, p)
    with pytest.raises(AppIdentityError):
        verify_google_id_token(t, client_id)

def test_google_needs_matching_aud(app):
    client_id = 'i.am.a.client'
    p = _valid_payload(client_id + '.but.a.wrong.one')
    t = _encode_valid_token(app, p)
    with pytest.raises(AppIdentityError):
        verify_google_id_token(t, client_id)

def test_google_needs_iat(app):
    client_id = 'i.am.a.client'
    p = _valid_payload(client_id)
    del p['iat']
    t = _encode_valid_token(app, p)
    with pytest.raises(AppIdentityError):
        verify_google_id_token(t, client_id)

def test_google_needs_valid_iat(app):
    client_id = 'i.am.a.client'
    p = _valid_payload(client_id)
    p['iat'] = datetime.datetime.utcnow() + datetime.timedelta(days=200)
    t = _encode_valid_token(app, p)
    with pytest.raises(AppIdentityError):
        verify_google_id_token(t, client_id)

def test_google_needs_exp(app):
    client_id = 'i.am.a.client'
    p = _valid_payload(client_id)
    del p['exp']
    t = _encode_valid_token(app, p)
    with pytest.raises(AppIdentityError):
        verify_google_id_token(t, client_id)

def test_google_needs_valid_exp(app):
    client_id = 'i.am.a.client'
    p = _valid_payload(client_id)
    p['exp'] = datetime.datetime.utcnow() - datetime.timedelta(days=200)
    t = _encode_valid_token(app, p)
    with pytest.raises(AppIdentityError):
        verify_google_id_token(t, client_id)
