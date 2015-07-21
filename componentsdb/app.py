import datetime
import os

import jwt

from flask import Flask, current_app
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    """Creates a new Flask application for the components DB. After loading
    configuration from componentsdb.default_settings, configuration is then loaded
    from the file specified by the COMPONENTSDB_SETTINGS environment variable if
    set.

    After registering any blueprints, call init_app() with the returned
    application to associate the db instance with the new application.

    """
    app = Flask(__name__)
    app.config.from_object('componentsdb.default_settings')
    if 'COMPONENTSDB_SETTINGS' in os.environ:
        app.config.from_envvar('COMPONENTSDB_SETTINGS')
    return app

def init_app(app):
    """Initialise an app returned by create_app()."""
    db.init_app(app)
    return app

def register_default_blueprints(app):
    """Register the default set of blueprints."""
    from componentsdb.api import api
    app.register_blueprint(api, url_prefix='/api')

def default_app():
    """Create and return the "default" app resulting from calls to create_app(),
    register_default_blueprints() and init_app().

    """
    app = create_app()
    register_default_blueprints(app)
    init_app(app)
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
