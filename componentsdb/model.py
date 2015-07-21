"""
SQLAlchemy models for the database.

"""
# pylint: disable=too-few-public-methods

import base64
import json

from componentsdb.app import db, jwt_encode, jwt_decode

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

class KeyDecodeError(Exception):
    pass

class _MixinEncodable(object):
    """A mixin which allows the object to be referenced by an encoded URL-safe
    id.

    """
    @property
    def encoded_key(self):
        """Return a URL-safe encoding of the primary key and table name."""
        # pylint: disable=no-member
        return _b64_encode(json.dumps(
            dict(t=self.__class__.__tablename__, id=self.id)
        ).encode('utf8'))

    @classmethod
    def decode_key(cls, k):
        """Decode a URL-safe encoded key for this model into a primary key.

        Raises KeyDecodeError if the key is correctly encoded but for the wrong
        table.

        """
        # pylint: disable=no-member
        d = json.loads(_b64_decode(k.encode('ascii')).decode('utf8'))
        if cls.__tablename__ != d['t']:
            raise KeyDecodeError('key is for incorrect table')
        return int(d['id'])

class _MixinsCommon(_MixinCreatedAt, _MixinWithId):
    pass

class Component(db.Model, _MixinsCommon, _MixinEncodable):
    __tablename__ = 'components'

    code = db.Column(db.Text)
    description = db.Column(db.Text)
    datasheet_url = db.Column(db.Text)

class Collection(db.Model, _MixinsCommon, _MixinEncodable):
    __tablename__ = 'collections'

    name = db.Column(db.Text, nullable=False)

class User(db.Model, _MixinsCommon, _MixinEncodable):
    __tablename__ = 'users'

    name = db.Column(db.Text, nullable=False)

    @property
    def token(self):
        """Return a JWT with this user as a claim."""
        return jwt_encode(dict(user=self.id))

    @classmethod
    def decode_token(cls, t):
        p = jwt_decode(t)
        return int(p['user'])

Permission = db.Enum('create', 'read', 'update', 'delete')

class UserCollectionPermission(db.Model, _MixinsCommon):
    __tablename__ = 'user_collection_perms'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    collection_id = db.Column(
        db.Integer, db.ForeignKey('collections.id'), nullable=False
    )
    permission = db.Column(Permission, nullable=False)

    user = db.relationship('User')
    collection = db.relationship('Collection')


