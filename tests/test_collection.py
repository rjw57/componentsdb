import pytest
from werkzeug.exceptions import NotFound

from componentsdb.model import Collection, Permission

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
