# pylint: disable=redefined-outer-name

import pytest

from componentsdb.model import (
    Collection, User, UserCollectionPermission, Permission
)
from componentsdb.query import user_collections

@pytest.fixture
def collections(mixer):
    return mixer.cycle(5).blend(Collection, name=mixer.FAKE)

@pytest.fixture
def users(mixer):
    return mixer.cycle(5).blend(User, name=mixer.FAKE)

@pytest.fixture
def perms(mixer, users, collections):
    # pylint: disable=unused-argument
    perms = mixer.cycle(15).blend(
        UserCollectionPermission,
        user=mixer.SELECT,
        collection=mixer.SELECT,
    )

    return perms

def test_user_collections_query(perms, users, collections, db, mixer):
    # pylint: disable=unused-argument
    c, u = collections[0], users[0]

    # ensure user has at least one read permission
    perm_id = mixer.blend(
        UserCollectionPermission, user=u, collection=c, permission='read'
    ).id

    # ensure all entities returned by query are valid
    q = user_collections(u, 'read')
    for _, _ucp in q.add_entity(UserCollectionPermission):
        assert _ucp.permission == 'read'
        assert _ucp.user_id == u.id

    # ensure at least one entity returned
    assert q.count() > 0

    # ensure that the permission we added is included
    assert q.filter(UserCollectionPermission.id == perm_id).count() == 1

def test_has_permission(user, collection):
    # User should have no permissions on the new collection
    assert not collection.has_permission(user, Permission.CREATE)
    assert not collection.has_permission(user, Permission.READ)
    assert not collection.has_permission(user, Permission.UPDATE)
    assert not collection.has_permission(user, Permission.DELETE)

def test_add_permission(user, collection):
    # User cannot read or update initially
    assert not collection.has_permission(user, Permission.READ)
    assert not collection.has_permission(user, Permission.UPDATE)

    # Allow user permission to read
    collection.add_permission(user, Permission.READ)

    # User can now read but still not update
    assert collection.has_permission(user, Permission.READ)
    assert not collection.has_permission(user, Permission.UPDATE)

def test_remove_permission(user, collection):
    # Allow user permission to read
    collection.add_permission(user, Permission.READ)

    # User can now read
    assert collection.has_permission(user, Permission.READ)

    # Revoke permission
    collection.remove_permission(user, Permission.READ)

    # User cannot now read
    assert not collection.has_permission(user, Permission.READ)

def test_remove_non_existant_permission(user, collection):
    """It should always be possible to remove a permission a user does not
    have."""
    assert not collection.has_permission(user, Permission.READ)
    collection.remove_permission(user, Permission.READ)
    assert not collection.has_permission(user, Permission.READ)

def test_add_duplicate_permission(user, collection):
    """It should always be possible to add a permission a user already has."""
    assert not collection.has_permission(user, Permission.READ)
    collection.add_permission(user, Permission.READ)
    assert collection.has_permission(user, Permission.READ)
    collection.add_permission(user, Permission.READ)
    assert collection.has_permission(user, Permission.READ)

def test_removes_all_permissions(user, collection):
    """Duplicate permissions are removed."""
    assert not collection.has_permission(user, Permission.READ)
    collection.add_permission(user, Permission.READ)
    collection.add_permission(user, Permission.READ)
    assert collection.has_permission(user, Permission.READ)
    collection.remove_permission(user, Permission.READ)
    assert not collection.has_permission(user, Permission.READ)

def test_can_create(current_user, collection):
    """Test can_create helper."""
    assert not collection.can_create
    collection.add_permission(current_user, Permission.CREATE)
    assert collection.can_create
    collection.remove_permission(current_user, Permission.CREATE)
    assert not collection.can_create

def test_can_read(current_user, collection):
    """Test can_read helper."""
    assert not collection.can_read
    collection.add_permission(current_user, Permission.READ)
    assert collection.can_read
    collection.remove_permission(current_user, Permission.READ)
    assert not collection.can_read

def test_can_update(current_user, collection):
    """Test can_update helper."""
    assert not collection.can_update
    collection.add_permission(current_user, Permission.UPDATE)
    assert collection.can_update
    collection.remove_permission(current_user, Permission.UPDATE)
    assert not collection.can_update

def test_can_delete(current_user, collection):
    """Test can_delete helper."""
    assert not collection.can_delete
    collection.add_permission(current_user, Permission.DELETE)
    assert collection.can_delete
    collection.remove_permission(current_user, Permission.DELETE)
    assert not collection.can_delete


