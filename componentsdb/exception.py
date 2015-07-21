"""
Custom exceptions used by the database.

"""
from werkzeug.exceptions import Unauthorized as _Unauthorized

class KeyDecodeError(Exception):
    pass

class KeyEncodeError(Exception):
    pass

class UnauthorizedError(_Unauthorized):
    pass
