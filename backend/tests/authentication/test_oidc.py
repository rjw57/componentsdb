import requests
from jwcrypto.jwk import JWKSet
from jwcrypto.jwt import JWT


def test_jwt_issuer(jwt_issuer: str, jwks_url: str):
    r = requests.get("".join([jwt_issuer.rstrip("/"), "/.well-known/openid-configuration"]))
    r.raise_for_status()
    assert r.json()["jwks_url"] == jwks_url


def test_oidc_token(oidc_token: str, jwk_set: JWKSet, jwt_issuer: str):
    jwt = JWT(check_claims={"iss": jwt_issuer})
    jwt.deserialize(oidc_token, jwk_set)
