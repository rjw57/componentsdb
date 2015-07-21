"""
JSON API blueprint.

"""
from functools import wraps

from flask import Blueprint, jsonify, request
from werkzeug.exceptions import Unauthorized, BadRequest

from componentsdb.auth import verify_user_token, current_user

api = Blueprint('api', __name__)

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

        verify_user_token(auth[1])

        return f(*args, **kwargs)
    return decorated

@api.route('/profile')
@auth_required
def profile():
    return jsonify(dict(name=current_user.name))
