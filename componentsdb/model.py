"""
SQLAlchemy models for the database.

"""
# pylint: disable=too-few-public-methods
import base64
import enum
import json

# pylint: disable=no-name-in-module,import-error
from flask.ext.sqlalchemy import SQLAlchemy
import sqlalchemy.types as types

db = SQLAlchemy()

# Mixin classes for common model functionality

class _ModelWithIdMixin(object):
    id = db.Column(db.Integer, primary_key=True)

class _ModelWithTimestampsMixin(object):
    created_at = db.Column(db.DateTime, server_default=db.FetchedValue())
    updated_at = db.Column(db.DateTime, server_default=db.FetchedValue())

class _CommonModelMixins(_ModelWithTimestampsMixin, _ModelWithIdMixin):
    pass

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

class Component(db.Model, _CommonModelMixins, _MixinEncodable):
    __tablename__ = 'components'

    code = db.Column(db.Text)
    description = db.Column(db.Text)
    datasheet_url = db.Column(db.Text)

class Collection(db.Model, _CommonModelMixins, _MixinEncodable):
    __tablename__ = 'collections'

    name = db.Column(db.Text, nullable=False)

    def _permissions_query(self, user, perm):
        q = UserCollectionPermission.query # pylint: disable=no-member
        q = q.filter(UserCollectionPermission.user_id == user.id)
        q = q.join(Collection).filter(Collection.id == self.id)
        q = q.filter(UserCollectionPermission.permission == perm)
        return q

    def has_permission(self, user, perm):
        """Return True iff the user has permission perm on this collection."""
        return self._permissions_query(user, perm).limit(1).count() > 0

    def add_permission(self, user, perm):
        """Add the permission perm on this collection to user user."""
        db.session.add(UserCollectionPermission(
            user=user, collection=self, permission=perm
        ))

    def remove_permission(self, user, perm):
        # pylint: disable=no-member
        s = self._permissions_query(user, perm).\
            with_entities(UserCollectionPermission.id)
        UserCollectionPermission.query.\
            filter(UserCollectionPermission.id.in_(s)).delete(False)

    # Below we need to import current_user within the function since auth itself
    # imports this module.

    @property
    def can_create(self):
        from componentsdb.auth import current_user
        return self.has_permission(current_user, Permission.CREATE)

    @property
    def can_read(self):
        from componentsdb.auth import current_user
        return self.has_permission(current_user, Permission.READ)

    @property
    def can_update(self):
        from componentsdb.auth import current_user
        return self.has_permission(current_user, Permission.UPDATE)

    @property
    def can_delete(self):
        from componentsdb.auth import current_user
        return self.has_permission(current_user, Permission.DELETE)

class User(db.Model, _CommonModelMixins, _MixinEncodable):
    __tablename__ = 'users'

    name = db.Column(db.Text, nullable=False)

    @property
    def token(self):
        """Return a JWT with this user as a claim."""
        from componentsdb.auth import jwt_encode
        return jwt_encode(dict(user=self.id))

    @classmethod
    def decode_token(cls, t):
        from componentsdb.auth import jwt_decode
        p = jwt_decode(t)
        return int(p['user'])

class Permission(enum.Enum):
    """Posssible permissions."""
    CREATE = 'create'
    READ = 'read'
    UPDATE = 'update'
    DELETE = 'delete'

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

_PermissionType = _decorate_enum_type(Permission)

class UserCollectionPermission(db.Model, _CommonModelMixins):
    __tablename__ = 'user_collection_perms'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    collection_id = db.Column(
        db.Integer, db.ForeignKey('collections.id'), nullable=False
    )
    permission = db.Column(_PermissionType, nullable=False)

    user = db.relationship('User')
    collection = db.relationship('Collection')


