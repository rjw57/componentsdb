"""
Settings for application when being run in the test suite.

"""
import os
import sys

# Add the directory containing this file to the search path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import function to generate a self-signed cert dynamically
from x509cert import gen_self_signed_cert

DEBUG = True
TESTING = True
SECRET_KEY = 'bonjour, monde'

# Configure the testing database. The database URI is specified by the
# COMPONENTSDB_DATABASE_URI environment variable.
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'COMPONENTSDB_DATABASE_URI', 'sqlite://'
)
SQLALCHEMY_ECHO = True

_cert, _key = gen_self_signed_cert()
GOOGLE_OAUTH2_CERTS = {'selfsigned': _cert}
TESTING_GOOGLE_OAUTH2_CERT_PRIV_KEYS = {'selfsigned', _key}

