import json

import pytest
from faker import Faker
from jwcrypto.jwk import JWK
from jwcrypto.jwt import JWT
from responses import RequestsMock

from componentsdb.authentication.transport.requests import caching_disabled


@pytest.fixture(autouse=True)
def disabled_request_cache():
    "Disable HTTP request caching in tests."
    with caching_disabled():
        yield


@pytest.fixture
def jwt_issuer(faker: Faker, jwks_uri: str, mocked_responses: RequestsMock) -> str:
    issuer_url = faker.url(schemes=["https"]).rstrip("/")
    discovery_doc = json.dumps({"jwks_uri": jwks_uri, "issuer": issuer_url}).encode("utf8")
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


def make_jwt(claims: dict[str, str], key: JWK, alg: str) -> str:
    jwt = JWT(header={"alg": alg, "kid": key["kid"], "type": "JWT"}, claims=claims)
    jwt.make_signed_token(key)
    return jwt.serialize()


@pytest.fixture(params=["ES256", "RS256"])
def oidc_token(request, oidc_claims: dict[str, str], jwks: dict[str, JWK]) -> str:
    return make_jwt(oidc_claims, jwks[request.param], request.param)
