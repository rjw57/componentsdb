"""
CLI management script. (Requires flask-script.)

"""
import os

# pylint: disable=no-name-in-module,import-error
from flask.ext.script import Manager
from flask.ext.migrate import MigrateCommand, Migrate

from componentsdb.app import default_app
from componentsdb.model import db

# Default to development environment settings unless told otherwise
if 'COMPONENTSDB_SETTINGS' not in os.environ:
    os.environ['COMPONENTSDB_SETTINGS'] = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'devsettings.py'
    )

app = default_app()
manager = Manager(app)
migrate = Migrate(app, db, directory='alembic')

manager.add_command('migrate', MigrateCommand)

if __name__ == "__main__":
    manager.run()

