import pytest

from componentsdb.model import User, Component
from componentsdb.exception import KeyDecodeError, KeyEncodeError

def test_encoded_key(user):
    # encode the key
    k = user.encoded_key
    assert k is not None

    # get id from key
    id_ = User.decode_key(k)
    assert id_ == user.id

def test_must_be_in_db(db):
    # pylint: disable=unused-argument

    # create a user which has not been added to the database
    u = User(name='bob')
    assert u.id is None

    with pytest.raises(KeyEncodeError):
        # encoding the key fails
        assert u.encoded_key is not None

def test_key_encodes_type(user):
    # decoding a User key as a Component should fail
    k = user.encoded_key
    with pytest.raises(KeyDecodeError):
        Component.decode_key(k)
