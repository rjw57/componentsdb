import logging

import pytest
from werkzeug.exceptions import NotFound

from componentsdb.model import Collection, Permission, ModelError

def test_get_requires_read(current_user, collection):
    # pylint: disable=no-member

    # make sure user has no read permission
    collection.remove_permission(current_user, Permission.READ)

    with pytest.raises(NotFound):
        _ = Collection.query.get_for_user_or_404(current_user, collection.id)

    # adding permission succeeds
    collection.add_permission(current_user, Permission.READ)
    c = Collection.query.get_for_user_or_404(current_user, collection.id)
    assert c is not None
    assert c.id == collection.id

def test_with_user_permission(user, mixer):
    """Collection can query collections with user permissions."""
    # Create some collections
    cs1 = mixer.cycle(10).blend(Collection)
    cs2 = mixer.cycle(5).blend(Collection)

    for c in cs1 + cs2:
        c.add_permission(user, Permission.READ)
    for c in cs2:
        c.add_permission(user, Permission.UPDATE)

    rs = Collection.query.with_user_permission(user, Permission.UPDATE).all()
    for r in rs:
        logging.info('has update: %s', r)
    assert len(rs) == len(cs2)

    rs = Collection.query.with_user_permission(user, Permission.READ).all()
    for r in rs:
        logging.info('has read: %s', r)
    assert len(rs) == len(cs1) + len(cs2)

def test_delete_needs_permission(current_user, collection):
    collection.add_all_permissions(current_user)
    collection.remove_permission(current_user, Permission.DELETE)
    with pytest.raises(ModelError):
        collection.delete()

def test_delete(current_user, collection):
    collection.add_all_permissions(current_user)
    assert collection.can_delete
    collection.delete()
    assert Collection.query.get(collection.id) is None
