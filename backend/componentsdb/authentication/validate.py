import json
from collections.abc import Callable, Collection, Sequence
from inspect import isawaitable
from typing import Any, Mapping, Optional, TypeAlias

import structlog

from . import oidc
from .policies import ExpectedUnverifiedAudiencePolicy, ExpectedUnverifiedIssuerPolicy
from .transport import AsyncRequestBase, RequestBase, requests

LOG = structlog.get_logger()

# A callable taking claims from an unvalidated token which raises InvalidClaimsError if the token
# should not be accepted.
UnvalidatedTokenPolicy: TypeAlias = Callable[[oidc.UnvalidatedClaims], None]

# A callable taking claims from a validated token which raises InvalidClaimsError if the token
# should not be accepted.
ValidatedTokenPolicy: TypeAlias = Callable[[Mapping[str, Any]], None]


class ValidateToken:
    """
    Validate an unvalidated token against validation policies. Policies may run before the token's
    signature if verified, in which case they are passed the unvalidated claims dict, or after
    signature verification, in which case they are passed the validated claims dict.

    Generally policies should run after validation. Exceptions include checking the audience and
    issuer claims match those expected so that we avoid making HTTP requests for tokens not meant
    for us.

    Validation policies which run asynchronously require that the async_validate method be used.

    Policies are run sequentially, even with asynchronous policies so that policies may be ordered
    from most general to least or most costly to least.

    Args:
        pre_validation_policies: validation policies to run before token signature is validated.
        post_validation_policies: validation policies to run after token signature is validated.
    """

    pre_validation_policies: Sequence[UnvalidatedTokenPolicy]
    post_validation_policies: Sequence[ValidatedTokenPolicy]

    def __init__(
        self,
        pre_validation_policies: Optional[Sequence[UnvalidatedTokenPolicy]] = None,
        post_validation_policies: Optional[Sequence[ValidatedTokenPolicy]] = None,
    ):
        self.pre_validation_policies = (
            pre_validation_policies if pre_validation_policies is not None else []
        )
        self.post_validation_policies = (
            post_validation_policies if post_validation_policies is not None else []
        )

    def validate(self, token: str, request: Optional[RequestBase] = None) -> Mapping[str, Any]:
        """
        Validate the token.

        Args:
            token: the token to validate.
            request: HTTP transport to use. Defaults to a caching requests-based transport.

        Returns:
            A dictionary of claims present in the token.

        Raises:
            AuthenticationError: if token failed validation.
            RuntimeError: if any policy returns an awaitable object rather than completing
                synchronously.
        """
        request = request if request is not None else requests.request
        unvalidated_claims = oidc.unvalidated_claims_from_token(token)
        for p in self.pre_validation_policies:
            if isawaitable(p(unvalidated_claims)):
                raise RuntimeError("Validation policy includes asynchronous callable.")
        jwt = oidc.validate_token(token, request)
        validated_claims = json.loads(jwt.claims)
        for p in self.post_validation_policies:
            if isawaitable(p(validated_claims)):
                raise RuntimeError("Validation policy includes asynchronous callable.")
        return validated_claims

    async def async_validate(
        self, token: str, request: Optional[AsyncRequestBase] = None
    ) -> Mapping[str, Any]:
        """
        Validate the token asynchronously.

        Args:
            token: the token to validate.
            request: HTTP transport to use. Defaults to a caching requests-based transport.

        Returns:
            A dictionary of claims present in the token.

        Raises:
            AuthenticationError: if token failed validation.
            RuntimeError: if any policy returns an awaitable object rather than completing
                synchronously.
        """
        request = request if request is not None else requests.async_request
        unvalidated_claims = oidc.unvalidated_claims_from_token(token)
        for p in self.pre_validation_policies:
            r = p(unvalidated_claims)
            if isawaitable(r):
                await r
        jwt = await oidc.async_validate_token(token, request)
        validated_claims = json.loads(jwt.claims)
        for p in self.post_validation_policies:
            r = p(validated_claims)
            if isawaitable(r):
                await r
        return validated_claims


def _default_pre_validation_policies(
    audiences: Collection[str],
    issuers: Collection[str],
):
    return [
        ExpectedUnverifiedAudiencePolicy(audiences),
        ExpectedUnverifiedIssuerPolicy(issuers),
    ]


def validate_token(
    token: str,
    *,
    audiences: Collection[str],
    issuers: Collection[str],
    request: Optional[RequestBase] = None,
):
    """
    Validate an authentication token. The token must have an "aud" claim which matches one of the
    provided audiences and an "iss" claim which matches one of the provided issuers.

    Args:
        token: incoming token to be validated
        audience: expected audiences for the token
        issuers: expected issuers for the token

    Raises:
        AuthenticationError: if the token cannot be validated.
    """
    return ValidateToken(
        pre_validation_policies=_default_pre_validation_policies(audiences, issuers),
    ).validate(token, request)


async def async_validate_token(
    token: str,
    *,
    audiences: Collection[str],
    issuers: Collection[str],
    request: Optional[AsyncRequestBase] = None,
):
    """
    Asynchronous variant of validate_token.
    """
    return await ValidateToken(
        pre_validation_policies=_default_pre_validation_policies(audiences, issuers),
    ).async_validate(token, request)
