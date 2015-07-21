import pytest

from componentsdb.model import User, Component

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
    with pytest.raises(TypeError):
        Component.decode_key(k)
