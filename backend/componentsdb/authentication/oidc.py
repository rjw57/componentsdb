import json
from collections.abc import Awaitable, Callable
from typing import NewType, TypeAlias, cast
from urllib.parse import urlparse

from jwcrypto.jwk import JWKSet
from jwcrypto.jwt import JWT
from validators.url import url as validate_url

from .exceptions import (
    InvalidIssuer,
    InvalidJWKSUrl,
    InvalidOIDCDiscoveryDocument,
    InvalidToken,
)

# These callables should raise FetchError if there is a problem fetching the URL or if the HTTP
# status code indicates an error.
FetchCallable: TypeAlias = Callable[[str], bytes]
AsyncFetchCallable: TypeAlias = Callable[[str], Awaitable[bytes]]

ValidatedIssuer = NewType("ValidatedIssuer", str)
ValidatedJWKSUrl = NewType("ValidatedJWKSUrl", str)


def validate_issuer(unvalidated_issuer: str) -> ValidatedIssuer:
    """
    Validate issuer is correctly formed.

    Args:
        unvalidated_issuer: issuer string which needs validating.

    Returns:
        The issuer if it is validated.

    Raises:
        InvalidIssuer: the issuer is not correctly formed.
    """
    if not validate_url(unvalidated_issuer):
        raise InvalidIssuer("Issuer is not valid URL.")
    if urlparse(unvalidated_issuer).scheme != "https":
        raise InvalidIssuer("Issuer does not have a https scheme.")
    return cast(ValidatedIssuer, unvalidated_issuer)


def validate_jwks_url(unvalidated_jwks_url: str) -> ValidatedJWKSUrl:
    """
    Validate JWKS URL is correctly formed.

    Args:
        unvalidated_jwks_url: URL which needs validating.

    Returns:
        The url if it is validated.

    Raises:
        InvalidJWKSUrl: the JWKS URL is not correctly formed.
    """
    if not validate_url(unvalidated_jwks_url):
        raise InvalidJWKSUrl("JWKS URL is not valid URL.")
    if urlparse(unvalidated_jwks_url).scheme != "https":
        raise InvalidJWKSUrl("JWKS URL does not have a https scheme.")
    return cast(ValidatedJWKSUrl, unvalidated_jwks_url)


def oidc_discovery_document_url(issuer: ValidatedIssuer) -> str:
    "Form an OIDC discovery document from a validated issuer."
    return "".join([issuer.rstrip("/"), "/.well-known/openid-configuration"])


def _jwks_url_from_oidc_discovery_document(
    expected_issuer: str, oidc_discovery_doc_content: bytes
) -> ValidatedJWKSUrl:
    try:
        oidc_discovery_doc = json.loads(oidc_discovery_doc_content)
    except json.JSONDecodeError as e:
        raise InvalidOIDCDiscoveryDocument(f"Error decoding OIDC discovery document: {e}")

    try:
        issuer = oidc_discovery_doc["issuer"]
    except KeyError:
        raise InvalidOIDCDiscoveryDocument("'issuer' key not present in OIDC discovery document.")
    if issuer != expected_issuer:
        raise InvalidOIDCDiscoveryDocument(
            f"Issuer {issuer!r} in OIDC discovery document does not "
            f"match expected issuer {expected_issuer!r}."
        )

    try:
        jwks_url = validate_jwks_url(oidc_discovery_doc["jwks_url"])
    except KeyError:
        raise InvalidOIDCDiscoveryDocument(
            "'jwks_url' key not present in OIDC discovery document."
        )
    return jwks_url


def fetch_jwks(unvalidated_issuer: str, fetch: FetchCallable) -> JWKSet:
    "Fetch a JWK set from an unvalidated issuer."
    oidc_discovery_doc = fetch(oidc_discovery_document_url(validate_issuer(unvalidated_issuer)))
    jwks_url = _jwks_url_from_oidc_discovery_document(unvalidated_issuer, oidc_discovery_doc)
    return JWKSet.from_json(fetch(jwks_url))


async def async_fetch_jwks(unvalidated_issuer: str, fetch: AsyncFetchCallable) -> JWKSet:
    "Fetch a JWK set from an unvalidated issuer using an asynchronous fetcher."
    oidc_discovery_doc = await fetch(
        oidc_discovery_document_url(validate_issuer(unvalidated_issuer))
    )
    jwks_url = _jwks_url_from_oidc_discovery_document(unvalidated_issuer, oidc_discovery_doc)
    return JWKSet.from_json(await fetch(jwks_url))


def unvalidated_issuer_from_token(unvalidated_token: str) -> str:
    "Parse and extract an unvalidated issuer from an unvalidated token."
    try:
        return json.loads(JWT.from_jose_token(unvalidated_token).token.objects["payload"])["iss"]
    except json.JSONDecodeError:
        raise InvalidToken("Could not decode token payload as JSON.")
    except KeyError:
        raise InvalidToken("Issuer claim cannot be read from token.")
