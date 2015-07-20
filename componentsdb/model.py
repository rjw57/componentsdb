"""
SQLAlchemy models for the database.

"""
import base64
import json

from sqlalchemy.ext.declarative import DeferredReflection
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class _MixinWithId(object):
    id = db.Column(db.Integer, primary_key=True)

class _MixinCreatedAt(object):
    created_at = db.Column(db.DateTime, server_default=db.FetchedValue())
    updated_at = db.Column(db.DateTime, server_default=db.FetchedValue())

def _b64_encode(bs):
    """Encode bytes to URL-safe base64 string stripping trailing '='s."""
    return base64.urlsafe_b64encode(bs).decode('utf8').rstrip('=')

def _b64_decode(s):
    """Decode bytes from URL-safe base64 inserting required padding."""
    padding = 4 - len(s)%4
    return base64.urlsafe_b64decode(s + b'='*padding)

class _MixinEncodable(object):
    """A mixin which allows the object to be referenced by an encoded URL-safe
    id.

    """
    @property
    def encoded_key(self):
        """Return a URL-safe encoding of the primary key and table name."""
        return _b64_encode(json.dumps(
            dict(t=self.__tablename__, id=self.id)
        ).encode('utf8'))

    @classmethod
    def decode_key(cls, k):
        """Decode a URL-safe encoded key for this model into a primary key.

        Raises TypeError if the key is correctly encoded but for the wrong
        table.

        """
        d = json.loads(_b64_decode(k.encode('ascii')).decode('utf8'))
        if cls.__tablename__ != d['t']:
            raise TypeError('key is for incorrect table')
        return int(d['id'])

class _MixinsCommon(_MixinCreatedAt, _MixinWithId):
    pass

class Component(db.Model, _MixinsCommon, _MixinEncodable):
    __tablename__ = 'components'
    code = db.Column(db.Text)
    description = db.Column(db.Text)
    datasheet_url = db.Column(db.Text)

class User(db.Model, _MixinsCommon, _MixinEncodable):
    __tablename__ = 'users'
    name = db.Column(db.Text, nullable=False)

Permission = db.Enum('create', 'read', 'update', 'delete')

class UserComponentPermission(db.Model, _MixinsCommon):
    __tablename__ = 'user_component_perms'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    component_id = db.Column(db.Integer, db.ForeignKey('components.id'),
            nullable=False)
    permission = db.Column(Permission, nullable=False)

    user = db.relationship('User')
    component = db.relationship('Component')


