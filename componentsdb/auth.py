from flask import _request_ctx_stack
from werkzeug.local import LocalProxy

from componentsdb.model import User

# A proxy for the current user.
current_user = LocalProxy(
    lambda: getattr(_request_ctx_stack.top, 'current_user', None)
)

def verify_user_token(token):
    """Verify token as a token for a user and, if valid, set the current_user in
    the request context. If the token is invalid either raise a JWT error or
    raise a 404 if the specified user is not found.

    """
    u = User.query.get_or_404(User.decode_token(token))
    _request_ctx_stack.top.current_user = u
