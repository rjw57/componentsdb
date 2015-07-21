"""
Settings for application when being run in the test suite.

"""
DEBUG = True
TESTING = True
SECRET_KEY = 'bonjour, monde'

SQLALCHEMY_ECHO = True
SQLALCHEMY_DATABASE_URI = 'postgres:///comp_testing'

