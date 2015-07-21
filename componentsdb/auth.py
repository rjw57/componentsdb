import datetime

import jwt
from flask import g as _flask_g, current_app
from werkzeug.local import LocalProxy

# A proxy for the current user.
current_user = LocalProxy(
    lambda: _flask_g.get('current_user', None)
)

def verify_user_token(token):
    """Verify token as a token for a user and, if valid, set the current_user in
    the request context. If the token is invalid either raise a JWT error or
    raise a 404 if the specified user is not found.

    """
    # pylint: disable=no-member
    from componentsdb.model import User
    u = User.query.get_or_404(User.decode_token(token))
    _flask_g.current_user = u

_JWT_ALGS = ['HS256']
_JWT_DEFAULT_EXP_DELTA = datetime.timedelta(hours=1)

def _jwt_encode_dangerous(payload):
    """Internal JWT encode function. Use jwt_encode() in preference."""
    secret = current_app.secret_key
    return jwt.encode(payload, secret, algorithm=_JWT_ALGS[0])

def jwt_encode(payload):
    # Make a shallow copy of the payload and set the exp field.
    p = {}
    p.update(payload)
    p['exp'] = datetime.datetime.utcnow() + _JWT_DEFAULT_EXP_DELTA
    return _jwt_encode_dangerous(p)

def jwt_decode(token):
    secret = current_app.secret_key
    return jwt.decode(
        token, secret, algorithms=_JWT_ALGS, options=dict(require_exp=True),
    )
