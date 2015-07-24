"""
Test JWT handling.

"""
# pylint: disable=redefined-outer-name, unused-argument

import datetime

import jwt
import pytest

from componentsdb.app import current_user, set_current_user_with_token
from componentsdb.model import (
    User,
    _jwt_encode, _jwt_decode, _jwt_encode_dangerous
)

def test_token_enc_dec(app):
    """Test basic encoding and decoding of token."""
    payload = dict(foo=1)
    t = _jwt_encode(payload)
    p = _jwt_decode(t)
    assert p['foo'] == 1

def test_token_has_exp(app):
    """Test that token has exp field in payload."""
    payload = dict(foo=1)
    t = _jwt_encode(payload)
    p = _jwt_decode(t)
    assert 'exp' in p

def test_verify_sig(app):
    """Test that token is verified."""
    payload = dict(foo=1)
    t = _jwt_encode(payload)
    old_key = app.secret_key
    try:
        app.secret_key = 'foo'
        with pytest.raises(jwt.exceptions.DecodeError):
            _jwt_decode(t)
    finally:
        app.secret_key = old_key

def test_verify_exp_in_future(app):
    """Test that token expiry is verified as being in future."""
    payload = dict(
        foo=1, exp=datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
    )
    t = _jwt_encode_dangerous(payload)
    with pytest.raises(jwt.exceptions.ExpiredSignatureError):
        _jwt_decode(t)

def test_verify_exp_present(app):
    """Test that token expiry is verified as being present."""
    payload = dict(foo=1)
    t = _jwt_encode_dangerous(payload)
    with pytest.raises(jwt.exceptions.MissingRequiredClaimError):
        _jwt_decode(t)

def test_user_token(user):
    """Users should be able to create tokens which refer to themselves."""
    t = user.token
    id_ = User.decode_token(t)
    assert id_ == user.id

def test_verify_user_token(user):
    """Verifying the current token should set current_user."""
    # NB: not "is None" since current_user is a proxy
    assert current_user == None
    t = user.token
    set_current_user_with_token(t)
    assert current_user.id == user.id

