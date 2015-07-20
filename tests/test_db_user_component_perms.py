import pytest

from componentsdb.model import Component, User, UserComponentPermission
from componentsdb.query import *

@pytest.fixture(scope='module')
def components(mixer):
    return mixer.cycle(5).blend(
        Component, code=mixer.FAKE, description=mixer.FAKE,
        datasheet_url=mixer.FAKE
    )

@pytest.fixture(scope='module')
def users(mixer):
    return mixer.cycle(5).blend(User, name=mixer.FAKE)

@pytest.fixture(scope='module')
def perms(mixer, users, components):
    perms = mixer.cycle(15).blend(
        UserComponentPermission,
        user=mixer.SELECT,
        component=mixer.SELECT,
    )

    return perms

def test_user_components_query(perms, users, components, db, mixer):
    c = components[0]
    u = users[0]

    # ensure user has at least one read permission
    perm_id = mixer.blend(
        UserComponentPermission, user=u, component=c, permission='read'
    ).id

    # ensure all entities returned by query are valid
    q = user_components(u, 'read')
    for _c, _ucp in q.add_entity(UserComponentPermission):
        assert _ucp.permission == 'read'
        assert _ucp.user_id == u.id

    # ensure at least one entity returned
    assert q.count() > 0

    # ensure that the permission we added is included
    assert q.filter(UserComponentPermission.id == perm_id).count() == 1
