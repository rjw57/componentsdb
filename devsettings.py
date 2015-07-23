"""
Settings for application when being run in developmenr.

"""
import os

DEBUG = True
SECRET_KEY = os.urandom(64)
SQLALCHEMY_DATABASE_URI = 'postgres:///componentsdb'

GOOGLE_CLIENT_ID = '428986687976-0ruhk16lejqffar0c59inhomps7458ol.apps.googleusercontent.com'
GOOGLE_OAUTH2_ALLOWED_CLIENT_IDS = [GOOGLE_CLIENT_ID]
