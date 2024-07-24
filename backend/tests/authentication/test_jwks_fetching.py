import pytest
from jwcrypto.jwk import JWKSet

from componentsdb.authentication import oidc
from componentsdb.authentication.transport.requests import async_fetch, fetch


def test_basic_case(jwt_issuer: str, jwk_set: JWKSet):
    fetched_jwk_set = oidc.fetch_jwks(jwt_issuer, fetch)
    assert fetched_jwk_set == jwk_set


@pytest.mark.asyncio
async def test_basic_case_async(jwt_issuer: str, jwk_set: JWKSet):
    fetched_jwk_set = await oidc.async_fetch_jwks(jwt_issuer, async_fetch)
    assert fetched_jwk_set == jwk_set
