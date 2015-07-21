import os

from flask import Flask

from componentsdb.api import api as _api
from componentsdb.model import db as _db

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
    app.register_blueprint(_api, url_prefix='/api')

def default_app():
    """Create and return the "default" app resulting from calls to create_app(),
    register_default_blueprints() and init_app().

    """
    app = create_app()
    register_default_blueprints(app)
    init_app(app)
    return app
