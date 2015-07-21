"""
SQLAlchemy models for the database.

"""
# pylint: disable=too-few-public-methods
import enum
import json

# pylint: disable=no-name-in-module,import-error
from flask.ext.sqlalchemy import SQLAlchemy
import sqlalchemy.types as types

from componentsdb._mixin import ModelWithEncodableKeyMixin

db = SQLAlchemy()

# Mixin classes for common model functionality

class _ModelWithIdMixin(object):
    id = db.Column(db.Integer, primary_key=True)

class _ModelWithTimestampsMixin(object):
    created_at = db.Column(db.DateTime, server_default=db.FetchedValue())
    updated_at = db.Column(db.DateTime, server_default=db.FetchedValue())

class _CommonModelMixins(_ModelWithTimestampsMixin, _ModelWithIdMixin):
    pass

# Utility functions

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

class User(db.Model, _CommonModelMixins, ModelWithEncodableKeyMixin):
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

class Component(db.Model, _CommonModelMixins, ModelWithEncodableKeyMixin):
    __tablename__ = 'components'

    code = db.Column(db.Text)
    description = db.Column(db.Text)
    datasheet_url = db.Column(db.Text)

class Collection(db.Model, _CommonModelMixins, ModelWithEncodableKeyMixin):
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

class Permission(enum.Enum):
    """Posssible permissions."""
    CREATE = 'create'
    READ = 'read'
    UPDATE = 'update'
    DELETE = 'delete'

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

