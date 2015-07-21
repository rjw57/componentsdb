"""
Tests the basic database invariants and constraints.
"""
# pylint: disable=redefined-outer-name,no-member
import logging

from componentsdb.model import (
    Component, User, Collection, UserCollectionPermission, Permission
)

def test_component_created_at(component):
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

def test_component_updated_at(db, component):
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

def test_user_created_at(user):
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

def test_user_updated_at(db, user):
    """Assert updated_at column is automatically updated by database."""
    # Update
    c = User.query.get(user.id)
    c.name = 'foobar'
    db.session.add(c)
    db.session.commit()

    # Retrieve
    c = User.query.get(c.id)
    assert c.name == 'foobar'

    logging.info('user %s created_at=%s', c.id, c.created_at)
    logging.info('user %s updated_at=%s', c.id, c.updated_at)
    assert c.updated_at > c.created_at

def test_collection_created_at(collection):
    """Assert created_at column is non-null in newly created collections and that
    updated_at matches it."""
    # Retrieve collection
    c = Collection.query.get(collection.id)
    assert c is not None

    # Check created at
    logging.info('collection %s created with created_at=%s', c.id, c.created_at)
    assert c.created_at is not None

    # Check updated_at
    logging.info('collection %s updated with updated_at=%s', c.id, c.updated_at)
    assert c.updated_at == c.created_at

def test_collection_updated_at(db, collection):
    """Assert updated_at column is automatically updated by database."""
    # Update
    c = Collection.query.get(collection.id)
    c.name = 'foobar'
    db.session.add(c)
    db.session.commit()

    # Retrieve
    c = Collection.query.get(c.id)
    assert c.name == 'foobar'

    logging.info('collection %s created_at=%s', c.id, c.created_at)
    logging.info('collection %s updated_at=%s', c.id, c.updated_at)
    assert c.updated_at > c.created_at

def test_user_collection_permission_created_at(user_collection_permission):
    """Assert created_at column is non-null in newly created
    user_collection_permissions and that updated_at matches it."""
    # Retrieve user_collection_permission
    c = UserCollectionPermission.query.get(user_collection_permission.id)
    assert c is not None

    # Check created at
    logging.info(
        'user_collection_permission %s created with created_at=%s',
        c.id, c.created_at
    )
    assert c.created_at is not None

    # Check updated_at
    logging.info(
        'user_collection_permission %s updated with updated_at=%s',
        c.id, c.updated_at
    )
    assert c.updated_at == c.created_at

def test_user_collection_permission_updated_at(db, user_collection_permission):
    """Assert updated_at column is automatically updated by database."""
    # Update
    c = UserCollectionPermission.query.get(user_collection_permission.id)

    p = c.permission
    new_p = Permission.UPDATE if p == Permission.READ else Permission.READ
    c.permission = new_p
    db.session.add(c)
    db.session.commit()

    # Retrieve
    c = UserCollectionPermission.query.get(c.id)
    assert c.permission == new_p

    logging.info(
        'user_collection_permission %s created_at=%s', c.id, c.created_at
    )
    logging.info(
        'user_collection_permission %s updated_at=%s', c.id, c.updated_at
    )
    assert c.updated_at > c.created_at
