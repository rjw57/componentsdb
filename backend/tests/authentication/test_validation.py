import pytest
from jwcrypto.jwk import JWK
from jwcrypto.jws import JWS
from jwcrypto.jwt import JWT

from componentsdb.authentication import exceptions, oidc


def test_oidc_token_issuer(oidc_token: str, jwt_issuer: str):
    assert oidc.unvalidated_issuer_from_token(oidc_token) == jwt_issuer


def test_token_payload_is_not_json(ec_jwk: JWK):
    jws = JWS("not json")
    jws.add_signature(
        ec_jwk, alg="ES256", protected={"alg": "ES256", "kid": ec_jwk["kid"], "type": "JWT"}
    )
    with pytest.raises(exceptions.InvalidToken):
        oidc.unvalidated_issuer_from_token(jws.serialize(compact=True))


def test_missing_issuer_claim(oidc_claims: dict[str, str], ec_jwk: JWK):
    del oidc_claims["iss"]
    jwt = JWT(
        header={"alg": "ES256", "kid": ec_jwk["kid"], "type": "JWT"},
        claims=oidc_claims,
    )
    jwt.make_signed_token(ec_jwk)
    token = jwt.serialize()
    with pytest.raises(exceptions.InvalidToken):
        oidc.unvalidated_issuer_from_token(token)
