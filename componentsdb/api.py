"""
JSON API blueprint.

"""
from functools import wraps

from flask import Blueprint, jsonify, request, url_for, current_app
from werkzeug.exceptions import Unauthorized, BadRequest

from componentsdb.app import current_user, set_current_user_with_token
from componentsdb.auth import user_for_google_id_token
from componentsdb.model import Collection, Permission

api = Blueprint('api', __name__)

def collection_to_resource(c):
    """Convert c to JSON-friendly dict."""
    key = c.encoded_key
    return dict(
        key=key, url=url_for('api.collection', key=key), name=c.name,
    )

def _get_json_or_400():
    """Return the JSON body from the request or raise BadRequest if the content
    tpye is incorrectly set."""
    j = request.get_json()
    if j is None:
        raise BadRequest
    return j

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', None)
        if auth is None:
            raise Unauthorized()

        auth = auth.split()
        if len(auth) != 2:
            raise BadRequest('Authorization header is >2 words')

        if auth[0].lower() != 'bearer':
            raise BadRequest('Authorization must be bearer token type')

        set_current_user_with_token(auth[1])

        return f(*args, **kwargs)
    return decorated

@api.route('/profile')
@auth_required
def profile():
    return jsonify(dict(name=current_user.name))

@api.route('/collections', methods=['GET', 'PUT'])
@auth_required
def collections():
    # pylint: disable=no-member
    q = Collection.query

    if request.method == 'PUT':
        c = q.get_or_404(Collection.create(_get_json_or_400()))
        return jsonify(collection_to_resource(c)), 201

    # Treat all other methods as "GET"

    # Where do we start?
    page_start = request.args.get('after')

    q = q.with_permission(Permission.READ).order_by(Collection.id)
    if page_start is not None and page_start != '':
        q = q.filter(Collection.id > Collection.decode_key(page_start))
    q = q.limit(current_app.config['PAGE_SIZE'])

    cs = list(q)
    page_end = cs[-1].encoded_key if len(cs) > 0 else page_start

    resources = [collection_to_resource(c) for c in cs]
    next_url = url_for('api.collections', after=page_end)

    return jsonify(dict(
        resources=resources, next=next_url,
    ))

@api.route('/collections/<key>')
@auth_required
def collection(key):
    # pylint: disable=no-member
    c = Collection.query.get_for_current_user_or_404(
        Collection.decode_key(key)
    )

    resource = dict(name=c.name)

    return jsonify(resource)

@api.route('/auth/exchange')
@auth_required
def exchange_token():
    """Exchange an auth token for a new one."""
    return jsonify(dict(token=current_user.token.decode('ascii')))

@api.route('/auth/google')
def exchange_google_token():
    """Exchange an google id token for a user token."""
    user = user_for_google_id_token(request.args['token'])
    return jsonify(dict(token=user.token.decode('ascii')))
