"""
Settings for application when being run in the test suite.

"""
import os

DEBUG = True
TESTING = True
SECRET_KEY = 'bonjour, monde'

# Configure the testing database. The database URI is specified by the
# COMPONENTSDB_DATABASE_URI environment variable.
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'COMPONENTSDB_DATABASE_URI', 'sqlite://'
)
SQLALCHEMY_ECHO = True
