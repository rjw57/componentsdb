import pytest

from componentsdb.model import User, Component
from componentsdb.exception import KeyDecodeError

def test_encoded_key(user):
    # encode the key
    k = user.encoded_key
    assert k is not None

    # get id from key
    id_ = User.decode_key(k)
    assert id_ == user.id

def test_key_encodes_type(user):
    # decoding a User key as a Component should fail
    k = user.encoded_key
    with pytest.raises(KeyDecodeError):
        Component.decode_key(k)
