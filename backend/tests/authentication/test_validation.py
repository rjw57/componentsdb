import datetime
from typing import Any

import pytest
from faker import Faker
from jwcrypto.jwk import JWK
from jwcrypto.jws import JWS
from jwcrypto.jwt import JWT

from componentsdb.authentication import async_validate_token
from componentsdb.authentication import exceptions as exc
from componentsdb.authentication import oidc, validate_token

from .oidc import make_jwt


def test_oidc_token_issuer(oidc_token: str, jwt_issuer: str):
    assert oidc.unvalidated_claim_from_token(oidc_token, "iss") == jwt_issuer


def test_token_payload_is_not_json(ec_jwk: JWK):
    jws = JWS("not json")
    jws.add_signature(
        ec_jwk, alg="ES256", protected={"alg": "ES256", "kid": ec_jwk["kid"], "type": "JWT"}
    )
    with pytest.raises(exc.InvalidTokenError):
        oidc.unvalidated_claim_from_token(jws.serialize(compact=True), "iss")


def test_missing_issuer_claim(oidc_claims: dict[str, str], ec_jwk: JWK):
    del oidc_claims["iss"]
    jwt = JWT(
        header={"alg": "ES256", "kid": ec_jwk["kid"], "type": "JWT"},
        claims=oidc_claims,
    )
    jwt.make_signed_token(ec_jwk)
    token = jwt.serialize()
    with pytest.raises(exc.InvalidTokenError):
        oidc.unvalidated_claim_from_token(token, "iss")


def test_basic_verification(faker: Faker, oidc_token: str, oidc_audience: str, jwt_issuer: str):
    validate_token(
        oidc_token, audiences=[faker.url(), oidc_audience], issuers=[faker.url(), jwt_issuer]
    )


@pytest.mark.asyncio
async def test_basic_async_verification(
    faker: Faker, oidc_token: str, oidc_audience: str, jwt_issuer: str
):
    await async_validate_token(
        oidc_token, audiences=[faker.url(), oidc_audience], issuers=[faker.url(), jwt_issuer]
    )


def test_mismatched_audience(faker: Faker, oidc_token: str, jwt_issuer: str):
    with pytest.raises(exc.InvalidClaimsError):
        validate_token(oidc_token, audiences=[faker.url()], issuers=[jwt_issuer])


def test_mismatched_issuer(faker: Faker, oidc_token: str, oidc_audience: str):
    with pytest.raises(exc.InvalidClaimsError):
        validate_token(oidc_token, audiences=[oidc_audience], issuers=[faker.url()])


@pytest.mark.parametrize("alg", ["RS256", "ES256"])
def test_bad_issuer_scheme(
    alg: str, faker: Faker, oidc_claims: dict[str, str], oidc_audience: str, jwks: dict[str, JWK]
):
    iss = faker.url(schemes=["http"])
    oidc_claims["iss"] = iss
    with pytest.raises(exc.InvalidIssuerError):
        validate_token(
            make_jwt(oidc_claims, jwks[alg], alg), audiences=[oidc_audience], issuers=[iss]
        )


@pytest.mark.parametrize("alg", ["RS256", "ES256"])
def test_issuer_not_url(
    alg: str, faker: Faker, oidc_claims: dict[str, str], oidc_audience: str, jwks: dict[str, JWK]
):
    iss = "not - a - url"
    oidc_claims["iss"] = iss
    with pytest.raises(exc.InvalidIssuerError):
        validate_token(
            make_jwt(oidc_claims, jwks[alg], alg), audiences=[oidc_audience], issuers=[iss]
        )


@pytest.mark.parametrize("alg", ["RS256", "ES256"])
def test_exp_claim_in_past(
    alg: str,
    faker: Faker,
    oidc_claims: dict[str, Any],
    oidc_audience: str,
    jwt_issuer: str,
    jwks: dict[str, JWK],
):
    oidc_claims["exp"] = datetime.datetime.now(datetime.UTC).timestamp() - 100000
    with pytest.raises(exc.InvalidTokenError):
        validate_token(
            make_jwt(oidc_claims, jwks[alg], alg), audiences=[oidc_audience], issuers=[jwt_issuer]
        )


@pytest.mark.parametrize("alg", ["RS256", "ES256"])
def test_nbf_claim_in_future(
    alg: str,
    faker: Faker,
    oidc_claims: dict[str, Any],
    oidc_audience: str,
    jwt_issuer: str,
    jwks: dict[str, JWK],
):
    oidc_claims["nbf"] = datetime.datetime.now(datetime.UTC).timestamp() + 100000
    with pytest.raises(exc.InvalidTokenError):
        validate_token(
            make_jwt(oidc_claims, jwks[alg], alg), audiences=[oidc_audience], issuers=[jwt_issuer]
        )
