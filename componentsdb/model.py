"""
SQLAlchemy models for the database.

"""
from sqlalchemy.ext.declarative import DeferredReflection
from flask.ext.sqlalchemy import SQLAlchemy

from componentsdb.app import app

db = SQLAlchemy(app)
db.reflect()

class Component(db.Model):
    __table__ = db.Table(
        'components', db.metadata,
        db.Column('created_at', db.DateTime, server_default=db.FetchedValue()),
        db.Column('updated_at', db.DateTime, server_default=db.FetchedValue()),
        extend_existing=True,
    )
