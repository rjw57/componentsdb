import datetime

import jwt

from flask import Flask, current_app
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    return app

_JWT_ALGS = [ 'HS256' ]
_JWT_DEFAULT_EXP_DELTA = datetime.timedelta(hours=1)

def _jwt_encode_dangerous(payload):
    """Internal JWT encode function. Use jwt_encode() in preference."""
    secret = current_app.secret_key
    return jwt.encode(payload, secret, algorithm=_JWT_ALGS[0])

def jwt_encode(payload):
    # Make a shallow copy of the payload and set the exp field.
    p = { }
    p.update(payload)
    p['exp'] = datetime.datetime.utcnow() + _JWT_DEFAULT_EXP_DELTA
    return _jwt_encode_dangerous(p)

def jwt_decode(token):
    secret = current_app.secret_key
    return jwt.decode(
        token, secret, algorithms=_JWT_ALGS, options=dict(require_exp=True),
    )
