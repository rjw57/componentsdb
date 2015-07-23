import os

from flask import Flask, g
from werkzeug.local import LocalProxy

from componentsdb.model import db as _db, User

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
    _db.init_app(app)
    return app

def register_default_blueprints(app):
    """Register the default set of blueprints."""
    from componentsdb.api import api
    from componentsdb.ui import ui
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(ui)

def default_app():
    """Create and return the "default" app resulting from calls to create_app(),
    register_default_blueprints() and init_app().

    """
    app = create_app()
    register_default_blueprints(app)
    init_app(app)
    return app

# User authentication

# A proxy for the current user.
current_user = LocalProxy(lambda: g.get('current_user', None))

def set_current_user_with_token(token):
    """Verify token as a token for a user and, if valid, set the current_user in
    the request context. If the token is invalid either raise a JWT error or
    raise a 404 if the specified user is not found.

    """
    # pylint: disable=no-member
    g.current_user = User.query.get_or_404(User.decode_token(token))
