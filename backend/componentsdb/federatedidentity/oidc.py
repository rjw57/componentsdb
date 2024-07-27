import json
from typing import Any, NewType, cast
from urllib.parse import urlparse

from jwcrypto.common import JWException
from jwcrypto.jwk import JWKSet
from jwcrypto.jwt import JWT
from validators.url import url as validate_url

from .exceptions import (
    InvalidIssuerError,
    InvalidJWKSUrlError,
    InvalidOIDCDiscoveryDocumentError,
    InvalidTokenError,
    TransportError,
)
from .transport import AsyncRequestBase, RequestBase

ValidatedIssuer = NewType("ValidatedIssuer", str)
ValidatedJWKSUrl = NewType("ValidatedJWKSUrl", str)
UnvalidatedClaims = NewType("UnvalidatedClaims", dict[str, Any])


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
        raise InvalidIssuerError("Issuer is not a valid URL.")
    if urlparse(unvalidated_issuer).scheme != "https":
        raise InvalidIssuerError("Issuer does not have a https scheme.")
    return cast(ValidatedIssuer, unvalidated_issuer)


def validate_jwks_uri(unvalidated_jwks_uri: str) -> ValidatedJWKSUrl:
    """
    Validate JWKS URL is correctly formed.

    Args:
        unvalidated_jwks_uri: URL which needs validating.

    Returns:
        The url if it is validated.

    Raises:
        InvalidJWKSUrl: the JWKS URL is not correctly formed.
    """
    if not validate_url(unvalidated_jwks_uri):
        raise InvalidJWKSUrlError("JWKS URL is not a valid URL.")
    if urlparse(unvalidated_jwks_uri).scheme != "https":
        raise InvalidJWKSUrlError("JWKS URL does not have a https scheme.")
    return cast(ValidatedJWKSUrl, unvalidated_jwks_uri)


def oidc_discovery_document_url(issuer: ValidatedIssuer) -> str:
    "Form an OIDC discovery document from a validated issuer."
    return "".join([issuer.rstrip("/"), "/.well-known/openid-configuration"])


def _jwks_uri_from_oidc_discovery_document(
    expected_issuer: str, oidc_discovery_doc_content: bytes
) -> ValidatedJWKSUrl:
    try:
        oidc_discovery_doc = json.loads(oidc_discovery_doc_content)
    except json.JSONDecodeError as e:
        raise InvalidOIDCDiscoveryDocumentError(f"Error decoding OIDC discovery document: {e}")

    try:
        issuer = oidc_discovery_doc["issuer"]
    except KeyError:
        raise InvalidOIDCDiscoveryDocumentError(
            "'issuer' key not present in OIDC discovery document."
        )
    if issuer != expected_issuer:
        raise InvalidOIDCDiscoveryDocumentError(
            f"Issuer {issuer!r} in OIDC discovery document does not "
            f"match expected issuer {expected_issuer!r}."
        )

    try:
        jwks_uri = validate_jwks_uri(oidc_discovery_doc["jwks_uri"])
    except KeyError:
        raise InvalidOIDCDiscoveryDocumentError(
            "'jwks_uri' key not present in OIDC discovery document."
        )
    return jwks_uri


def _request_json(url: str, request: RequestBase) -> bytes:
    """
    Wrapper arround RequestBase which requests a JSON document and raises TransportError on an
    error status code. The requested JSON document is not parsed.

    Returns:
        The response contents.
    """
    r = request(url, headers={"Accept": "application/json"})
    if r.status_code >= 400:
        raise TransportError(
            f"Error status when requesting {url!r}: {r.status_code}",
        )
    return r.content


async def _async_request_json(url: str, request: AsyncRequestBase) -> bytes:
    """
    Wrapper arround RequestBase which requests a JSON document and raises TransportError on an
    error status code. The requested JSON document is not parsed.

    Returns:
        The response contents.
    """
    r = await request(url, headers={"Accept": "application/json"})
    if r.status_code >= 400:
        raise TransportError(
            f"Error status when requesting {url!r}: {r.status_code}",
        )
    return r.content


def fetch_jwks(unvalidated_issuer: str, request: RequestBase) -> JWKSet:
    "Fetch a JWK set from an unvalidated issuer."
    oidc_discovery_doc = _request_json(
        oidc_discovery_document_url(validate_issuer(unvalidated_issuer)), request
    )
    jwks_uri = _jwks_uri_from_oidc_discovery_document(unvalidated_issuer, oidc_discovery_doc)
    return JWKSet.from_json(_request_json(jwks_uri, request))


async def async_fetch_jwks(unvalidated_issuer: str, request: AsyncRequestBase) -> JWKSet:
    "Fetch a JWK set from an unvalidated issuer using an asynchronous fetcher."
    oidc_discovery_doc = await _async_request_json(
        oidc_discovery_document_url(validate_issuer(unvalidated_issuer)), request
    )
    jwks_uri = _jwks_uri_from_oidc_discovery_document(unvalidated_issuer, oidc_discovery_doc)
    return JWKSet.from_json(await _async_request_json(jwks_uri, request))


def unvalidated_claims_from_token(unvalidated_token: str) -> UnvalidatedClaims:
    "Parse and extract unverified claims from the token."
    try:
        payload = json.loads(JWT.from_jose_token(unvalidated_token).token.objects["payload"])
    except json.JSONDecodeError:
        raise InvalidTokenError("Could not decode token payload as JSON.")
    if not isinstance(payload, dict):
        raise InvalidTokenError("Token claims are not a dictionary.")
    return cast(UnvalidatedClaims, payload)


def unvalidated_claim_from_token(unvalidated_token: str, claim: str) -> str:
    "Parse and extract an unvalidated claim from an unvalidated token."
    claims = unvalidated_claims_from_token(unvalidated_token)
    try:
        return claims[claim]
    except KeyError:
        raise InvalidTokenError(f"Claim '{claim}' not present in token paylaod.")


def _make_and_validate_token(unvalidated_token: str, jwk_set: JWKSet) -> JWT:
    try:
        jwt = JWT.from_jose_token(unvalidated_token)
        jwt.validate(jwk_set)
    except JWException as e:
        raise InvalidTokenError(f"Invalid token: {e}")
    return jwt


def validate_token(unvalidated_token: str, request: RequestBase) -> JWT:
    unvalidated_issuer = unvalidated_claim_from_token(unvalidated_token, "iss")
    jwk_set = fetch_jwks(unvalidated_issuer, request)
    return _make_and_validate_token(unvalidated_token, jwk_set)


async def async_validate_token(unvalidated_token: str, request: AsyncRequestBase) -> JWT:
    unvalidated_issuer = unvalidated_claim_from_token(unvalidated_token, "iss")
    jwk_set = await async_fetch_jwks(unvalidated_issuer, request)
    return _make_and_validate_token(unvalidated_token, jwk_set)
