import base64

from flask import json

from componentsdb.exception import KeyDecodeError

def _b64_encode(bs):
    """Encode bytes to URL-safe base64 string stripping trailing '='s."""
    return base64.urlsafe_b64encode(bs).decode('utf8').rstrip('=')

def _b64_decode(s):
    """Decode bytes from URL-safe base64 inserting required padding."""
    padding = 4 - len(s)%4
    return base64.urlsafe_b64decode(s + b'='*padding)

class ModelWithEncodableKeyMixin(object):
    """A mixin which allows the object to be referenced by an encoded URL-safe
    id.

    """
    @property
    def encoded_key(self):
        """Return a URL-safe encoding of the primary key and table name."""
        # pylint: disable=no-member
        return _b64_encode(json.dumps(
            dict(t=self.__class__.__tablename__, id=self.id)
        ).encode('utf8'))

    @classmethod
    def decode_key(cls, k):
        """Decode a URL-safe encoded key for this model into a primary key.

        Raises KeyDecodeError if the key is correctly encoded but for the wrong
        table.

        """
        # pylint: disable=no-member
        d = json.loads(_b64_decode(k.encode('ascii')).decode('utf8'))
        if cls.__tablename__ != d['t']:
            raise KeyDecodeError('key is for incorrect table')
        return int(d['id'])
