"""
CLI management script. (Requires flask-script.)

"""
import os

# pylint: disable=no-name-in-module,import-error
from flask.ext.script import Manager

from componentsdb.app import default_app

# Default to testing environment settings unless told otherwise
if 'COMPONENTSDB_SETTINGS' not in os.environ:
    os.environ['COMPONENTSDB_SETTINGS'] = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'tests', 'settings.py'
    )

app = default_app()
manager = Manager(app)

if __name__ == "__main__":
    manager.run()

