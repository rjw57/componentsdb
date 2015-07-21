"""
JSON API blueprint.

"""
from functools import wraps

from flask import Blueprint, jsonify, request, url_for
from werkzeug.exceptions import Unauthorized, BadRequest

from componentsdb.app import current_user, set_current_user_with_token
from componentsdb.model import Collection

api = Blueprint('api', __name__)

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
    if request.method == 'PUT':
        # create a collection and assign the current user all permissions
        c = Collection.create(_get_json_or_400())

        key = c.encoded_key
        return jsonify(dict(
            key=key, url=url_for('api.collection', key=key),
        )), 201

    # Treat all other methods as "GET"
    return jsonify({})

@api.route('/collections/<key>')
@auth_required
def collection(key):
    # pylint: disable=no-member
    c = Collection.query.get_for_current_user_or_404(
        Collection.decode_key(key)
    )

    resource = dict(name=c.name)

    return jsonify(resource)
