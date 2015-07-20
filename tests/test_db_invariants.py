"""
Tests the basic database invariants and constraints.
"""
import logging

import psycopg2
import pytest

from flask import Flask
from mixer.backend.flask import Mixer

from componentsdb.model import Component, User

@pytest.fixture
def component(db, mixer):
    """A newly inserted component with random values."""
    c = mixer.blend(
        Component, code=mixer.FAKE, description=mixer.FAKE,
        datasheet_url=mixer.FAKE,
    )
    return c

@pytest.fixture
def user(db, mixer):
    """A newly inserted user with random values."""
    u = mixer.blend(User, name=mixer.FAKE)
    return u

def test_component_created_at(db, mixer, component):
    """Assert created_at column is non-null in newly created components and that
    updated_at matches it."""
    # Retrieve component
    c = Component.query.get(component.id)
    assert c is not None

    # Check created at
    logging.info('component %s created with created_at=%s', c.id, c.created_at)
    assert c.created_at is not None

    # Check updated_at
    logging.info('component %s updated with updated_at=%s', c.id, c.updated_at)
    assert c.updated_at == c.created_at

def test_component_updated_at(db, mixer, component):
    """Assert updated_at column is automatically updated by database."""
    # Update
    c = Component.query.get(component.id)
    c.code = 'foobar'
    db.session.add(c)
    db.session.commit()

    # Retrieve
    c = Component.query.get(c.id)
    assert c.code == 'foobar'

    logging.info('component %s created_at=%s', c.id, c.created_at)
    logging.info('component %s updated_at=%s', c.id, c.updated_at)
    assert c.updated_at > c.created_at

def test_user_created_at(db, mixer, user):
    """Assert created_at column is non-null in newly created users and that
    updated_at matches it."""
    # Retrieve user
    c = User.query.get(user.id)
    assert c is not None

    # Check created at
    logging.info('user %s created with created_at=%s', c.id, c.created_at)
    assert c.created_at is not None

    # Check updated_at
    logging.info('user %s updated with updated_at=%s', c.id, c.updated_at)
    assert c.updated_at == c.created_at

def test_user_updated_at(db, mixer, user):
    """Assert updated_at column is automatically updated by database."""
    # Update
    c = User.query.get(user.id)
    c.name = 'foobar'
    db.session.add(c)
    db.session.commit()

    # Retrieve
    c = Component.query.get(c.id)
    assert c.code == 'foobar'

    logging.info('user %s created_at=%s', c.id, c.created_at)
    logging.info('user %s updated_at=%s', c.id, c.updated_at)
    assert c.updated_at > c.created_at
