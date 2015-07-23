"""
Traditional Web UI.

"""
from functools import wraps

from flask import (
    Blueprint, redirect, url_for, render_template, request, session
)
from werkzeug.exceptions import BadRequest, Unauthorized

from componentsdb.app import set_current_user_with_token
from componentsdb.auth import user_for_google_id_token

ui = Blueprint(
    'ui', __name__, template_folder='ui/templates', static_folder='ui/static',
    static_url_path='/ui_static',
)

AUTH_TOKEN_SESSION_KEY = 'componentsdb_auth'

def try_verify_session():
    """Like verify_session but return a boolean indicating success rather than
    raising an exception."""
    try:
        verify_session()
    except Unauthorized:
        return False
    return True

def verify_session():
    """Verify the authorisation in the current session. Raises Unauthorized if
    the session is not authorised. Sets current_user if the session is
    authorised.
    """
    t = session.get(AUTH_TOKEN_SESSION_KEY)
    if t is None:
        raise Unauthorized('no user token provided')
    set_current_user_with_token(t)

def auth_or_signin(f):
    """Decorator for a view which re-directs to the sign in page if there is no
    current user. The sign in page is given a query string which requests the
    current URL as the redirect."""
    @wraps(f)
    def view(*args, **kwargs):
        if not try_verify_session():
            return redirect(url_for('ui.signin', target=request.url))
        return f(*args, **kwargs)
    return view

@ui.route('/')
@auth_or_signin
def index():
    return 'hello, world'

@ui.route('/auth/signin')
def signin():
    redir_url = request.args.get('target', url_for('ui.index'))

    # Already signed in?
    if try_verify_session():
        return redirect(redir_url)

    # Have we been given a token?
    token = request.args.get('token', None)
    if token is not None:
        set_current_user_with_token(token)
        return redirect(redir_url)

    # Show sign in
    return render_template('signin.html')

@ui.route('/auth/google')
def signin_with_google_token():
    redir_url = request.args.get('target', url_for('ui.index'))

    token = request.args.get('token', None)
    if token is None:
        raise BadRequest('no token given')

    # Get auth token and add to session
    user = user_for_google_id_token(request.args['token'])
    session[AUTH_TOKEN_SESSION_KEY] = user.token

    # Redirect to sign in
    return redirect(redir_url)
