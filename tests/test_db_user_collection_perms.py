import pytest

from componentsdb.model import Collection, User, UserCollectionPermission
from componentsdb.query import *

@pytest.fixture(scope='module')
def collections(mixer):
    return mixer.cycle(5).blend(Collection, name=mixer.FAKE)

@pytest.fixture(scope='module')
def users(mixer):
    return mixer.cycle(5).blend(User, name=mixer.FAKE)

@pytest.fixture(scope='module')
def perms(mixer, users, collections):
    perms = mixer.cycle(15).blend(
        UserCollectionPermission,
        user=mixer.SELECT,
        collection=mixer.SELECT,
    )

    return perms

def test_user_collections_query(perms, users, collections, db, mixer):
    c = collections[0]
    u = users[0]

    # ensure user has at least one read permission
    perm_id = mixer.blend(
        UserCollectionPermission, user=u, collection=c, permission='read'
    ).id

    # ensure all entities returned by query are valid
    q = user_collections(u, 'read')
    for _c, _ucp in q.add_entity(UserCollectionPermission):
        assert _ucp.permission == 'read'
        assert _ucp.user_id == u.id

    # ensure at least one entity returned
    assert q.count() > 0

    # ensure that the permission we added is included
    assert q.filter(UserCollectionPermission.id == perm_id).count() == 1
