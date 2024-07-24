import json

import pytest
from faker import Faker
from jwcrypto.jwk import JWK
from jwcrypto.jwt import JWT
from responses import RequestsMock


@pytest.fixture
def jwt_issuer(faker: Faker, jwks_url: str, mocked_responses: RequestsMock) -> str:
    issuer_url = faker.url(schemes=["https"]).rstrip("/")
    discovery_doc = json.dumps({"jwks_url": jwks_url, "issuer": issuer_url}).encode("utf8")
    discovery_doc_url = f"{issuer_url}/.well-known/openid-configuration"
    mocked_responses.get(discovery_doc_url, body=discovery_doc, content_type="application/json")
    return issuer_url


@pytest.fixture
def oidc_subject(faker: Faker) -> str:
    return faker.slug()


@pytest.fixture
def oidc_audience(faker: Faker) -> str:
    return faker.slug()


@pytest.fixture
def oidc_claims(jwt_issuer: str, oidc_subject: str, oidc_audience: str) -> dict[str, str]:
    return {
        "iss": jwt_issuer,
        "sub": oidc_subject,
        "aud": oidc_audience,
    }


@pytest.fixture
def oidc_token(oidc_claims: dict[str, str], ec_jwk: JWK) -> str:
    jwt = JWT(
        header={"alg": "ES256", "kid": ec_jwk["kid"], "type": "JWT"},
        claims=oidc_claims,
    )
    jwt.make_signed_token(ec_jwk)
    return jwt.serialize()
