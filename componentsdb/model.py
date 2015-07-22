"""
SQLAlchemy models for the database.

"""
# pylint: disable=too-few-public-methods,no-name-in-module,import-error

import base64
import datetime
import enum

import jwt
from flask import g, json, current_app
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import func, types, type_coerce

from componentsdb.exception import KeyDecodeError, KeyEncodeError

db = SQLAlchemy()

# Mixin classes for common model functionality

class _IdMixin(object):
    id = db.Column(db.BigInteger, primary_key=True)

class _TimestampsMixin(object):
    created_at = db.Column(db.DateTime, server_default=db.FetchedValue())
    updated_at = db.Column(db.DateTime, server_default=db.FetchedValue())

class _EncodableKeyMixin(object):
    """A mixin which allows the object to be referenced by an encoded URL-safe
    id.

    """
    @property
    def encoded_key(self):
        """Return a URL-safe encoding of the primary key and table name. If the
        object is not in the database (id is None), raise KeyEncodeError."""
        # pylint: disable=no-member
        if self.id is None:
            raise KeyEncodeError('object not added to database')
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

class _CommonMixins(_TimestampsMixin, _IdMixin):
    pass

# Utility functions

def _b64_encode(bs):
    """Encode bytes to URL-safe base64 string stripping trailing '='s."""
    return base64.urlsafe_b64encode(bs).decode('utf8').rstrip('=')

def _b64_decode(s):
    """Decode bytes from URL-safe base64 inserting required padding."""
    padding = 4 - len(s)%4
    return base64.urlsafe_b64decode(s + b'='*padding)

_JWT_ALGS = ['HS256']
_JWT_DEFAULT_EXP_DELTA = datetime.timedelta(hours=1)

def _jwt_encode_dangerous(payload):
    """Internal JWT encode function. Use jwt_encode() in preference."""
    secret = current_app.secret_key
    return jwt.encode(payload, secret, algorithm=_JWT_ALGS[0])

def _jwt_encode(payload):
    # Make a shallow copy of the payload and set the exp field.
    p = {}
    p.update(payload)
    p['exp'] = datetime.datetime.utcnow() + _JWT_DEFAULT_EXP_DELTA
    return _jwt_encode_dangerous(p)

def _jwt_decode(token):
    secret = current_app.secret_key
    return jwt.decode(
        token, secret, algorithms=_JWT_ALGS, options=dict(require_exp=True),
    )

def _decorate_enum_type(enum_class):
    class _EnumTypeDecorator(types.TypeDecorator):
        """A SQLAlchemy TypeDecorator for 3.4-style enums."""
        # pylint: disable=abstract-method

        impl = db.Enum(*(m.value for m in enum_class))

        def process_bind_param(self, value, dialect):
            return value.value

        def process_result_value(self, value, dialect):
            return enum_class(value)
    return _EnumTypeDecorator

# The database models themselves

class User(db.Model, _CommonMixins, _EncodableKeyMixin):
    __tablename__ = 'users'

    name = db.Column(db.Text, nullable=False)

    @property
    def token(self):
        """Return a JWT with this user as a claim."""
        return _jwt_encode(dict(user=self.id))

    @classmethod
    def decode_token(cls, t):
        p = _jwt_decode(t)
        return int(p['user'])

class Component(db.Model, _CommonMixins, _EncodableKeyMixin):
    __tablename__ = 'components'

    code = db.Column(db.Text)
    description = db.Column(db.Text)
    datasheet_url = db.Column(db.Text)

class _CollectionQuery(db.Query):
    # pylint: disable=no-init

    def get_for_user_or_404(self, user, id_):
        """Get the collection specified by id but only if the user has read
        permissions."""
        return self.with_user_permission(user, Permission.READ).\
            filter(Collection.id == id_).first_or_404()

    def get_for_current_user_or_404(self, id_):
        """Get collection specified by id but only if the current user has
        read permissions."""
        return self.get_for_user_or_404(g.current_user, id_)

    def with_user_permission(self, user, perm):
        """Query collections where user has specified permission."""
        # pylint: disable=no-member
        return self.join(UserCollectionPermission).\
            filter(UserCollectionPermission.user_id == user.id).\
            filter(UserCollectionPermission.permission == perm)

    def with_permission(self, perm):
        """Query collections where *current* user has specified permission."""
        return self.with_user_permission(g.current_user, perm)

class Collection(db.Model, _CommonMixins, _EncodableKeyMixin):
    __tablename__ = 'collections'
    query_class = _CollectionQuery

    name = db.Column(db.Text, nullable=False)

    @classmethod
    def create(cls, body):
        """Create a new collection as the current user using the resource
        specified in the dict-like body. Raises a HTTPException on error.
        Returns the id of the new collection/

        """
        return db.session.query(func.collection_create(
            g.current_user.id, body.get('name')
        )).one()[0]

    def has_permission(self, user, perm):
        """Return True iff the user has permission perm on this collection."""
        return db.session.query(func.collection_user_has_permission(
            self.id, user.id, type_coerce(perm, _PermissionType)
        )).one()[0]

    def add_permission(self, user, perm):
        """Add the permission perm on this collection to user user."""
        db.session.query(func.collection_add_permission(
            self.id, user.id, type_coerce(perm, _PermissionType)
        )).one()

    def add_all_permissions(self, user):
        """Add all permissions to user on this collection."""
        for p in Permission:
            self.add_permission(user, p)

    def remove_permission(self, user, perm):
        db.session.query(func.collection_remove_permission(
            self.id, user.id, type_coerce(perm, _PermissionType)
        )).one()

    @property
    def can_create(self):
        return self.has_permission(g.current_user, Permission.CREATE)

    @property
    def can_read(self):
        return self.has_permission(g.current_user, Permission.READ)

    @property
    def can_update(self):
        return self.has_permission(g.current_user, Permission.UPDATE)

    @property
    def can_delete(self):
        return self.has_permission(g.current_user, Permission.DELETE)

class Permission(enum.Enum):
    """Posssible permissions."""
    CREATE = 'create'
    READ = 'read'
    UPDATE = 'update'
    DELETE = 'delete'

_PermissionType = _decorate_enum_type(Permission)

class UserCollectionPermission(db.Model, _CommonMixins):
    __tablename__ = 'user_collection_perms'

    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    collection_id = db.Column(
        db.BigInteger, db.ForeignKey('collections.id'), nullable=False
    )
    permission = db.Column(_PermissionType, nullable=False)

    user = db.relationship('User')
    collection = db.relationship('Collection')

class UserIdentity(db.Model, _CommonMixins):
    __tablename__ = 'user_identities'

    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    provider = db.Column(db.Text, nullable=False)
    provider_identity = db.Column(db.Text, nullable=False)

    user = db.relationship('User')
