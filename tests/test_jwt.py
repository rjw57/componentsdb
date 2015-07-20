"""
Test JWT handling.

"""
import datetime
from contextlib import contextmanager

import jwt
import pytest

from componentsdb.app import jwt_encode, jwt_decode, _jwt_encode_dangerous
from componentsdb.auth import verify_user_token, current_user
from componentsdb.model import User

@contextmanager
def secret(app, new_secret):
    """Simple context manager to temporarily change app's secret key."""
    old_secret = app.secret_key
    app.secret_key = new_secret
    yield
    app.secret_key = old_secret

def test_token_enc_dec(app):
    """Test basic encoding and decoding of token."""
    payload = dict(foo=1)
    t = jwt_encode(payload)
    p = jwt_decode(t)
    assert p['foo'] == 1

def test_token_has_exp(app):
    """Test that token has exp field in payload."""
    payload = dict(foo=1)
    t = jwt_encode(payload)
    p = jwt_decode(t)
    assert 'exp' in p

def test_verify_sig(app):
    """Test that token is verified."""
    payload = dict(foo=1)
    t = jwt_encode(payload)
    with secret(app, 'foo'), pytest.raises(jwt.exceptions.DecodeError):
        jwt_decode(t)

def test_verify_exp_in_future(app):
    """Test that token expiry is verified as being in future."""
    payload = dict(
        foo=1, exp=datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
    )
    t = _jwt_encode_dangerous(payload)
    with pytest.raises(jwt.exceptions.ExpiredSignatureError):
        jwt_decode(t)

def test_verify_exp_present(app):
    """Test that token expiry is verified as being present."""
    payload = dict(foo=1)
    t = _jwt_encode_dangerous(payload)
    with pytest.raises(jwt.exceptions.MissingRequiredClaimError):
        jwt_decode(t)

def test_user_token(user):
    """Users should be able to create tokens which refer to themselves."""
    t = user.token
    id = User.decode_token(t)
    assert id == user.id

def test_verify_user_token(user):
    """Verifying the current token should set current_user."""
    # NB: not "is None" since current_user is a proxy
    assert current_user == None
    t = user.token
    verify_user_token(t)
    assert current_user.id == user.id

