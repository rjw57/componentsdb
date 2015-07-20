"""
SQLAlchemy models for the database.

"""
from sqlalchemy.ext.declarative import DeferredReflection
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class _MixinWithId(object):
    id = db.Column(db.Integer, primary_key=True)

class _MixinCreatedAt(object):
    created_at = db.Column(db.DateTime, server_default=db.FetchedValue())
    updated_at = db.Column(db.DateTime, server_default=db.FetchedValue())

class Component(db.Model, _MixinCreatedAt, _MixinWithId):
    __tablename__ = 'components'
    code = db.Column(db.Text)
    description = db.Column(db.Text)
    datasheet_url = db.Column(db.Text)

class User(db.Model, _MixinCreatedAt, _MixinWithId):
    __tablename__ = 'users'
    name = db.Column(db.Text)

class UserComponentPermission(db.Model, _MixinCreatedAt, _MixinWithId):
    __tablename__ = 'user_component_perms'

