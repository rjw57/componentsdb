import httplib2
from flask import current_app, json
from oauth2client import client, crypt
from werkzeug.exceptions import HTTPException

_DEFAULT_GOOGLE_CERTS_URI = 'https://www.googleapis.com/oauth2/v1/certs'
_GOOGLE_ISSUERS = ['accounts.google.com', 'https://accounts.google.com']

_cached_http = httplib2.Http(client.MemoryCache())

def _get_default_certs():
    uri = current_app.config.get(
        'GOOGLE_OAUTH2_CERTS_URI', _DEFAULT_GOOGLE_CERTS_URI
    )
    r, content = _cached_http.request(uri)
    if r.status == 200:
        return json.loads(content)

    raise HTTPException(status_code=r.status) # pragma: no cover

def verify_google_id_token(token):
    """Verify the id token against the Google public keys. Note that this
    function does *not* validate the hosted domain (hd) claim. It *does* verify
    the issuer (iss) claim.

    If verification fails, an oauth2client.crypt.AppIdentityError is raised.
    """
    certs = current_app.config.get('GOOGLE_OAUTH2_CERTS', _get_default_certs())
    client_ids = current_app.config.get('GOOGLE_OAUTH2_ALLOWED_CLIENT_IDS', [])
    idinfo = crypt.verify_signed_jwt_with_certs(token, certs, None)
    if idinfo.get('aud') not in client_ids:
        raise crypt.AppIdentityError('invalid aud: %s' % idinfo.get('aud'))
    if idinfo.get('iss') not in _GOOGLE_ISSUERS:
        raise crypt.AppIdentityError('invalid issuer: %s' % idinfo.get('iss'))
    return idinfo
