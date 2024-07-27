from collections.abc import Collection
from typing import Any

import structlog

from . import oidc
from .exceptions import InvalidClaimsError

LOG = structlog.get_logger()


class ExpectedUnverifiedClaimsPolicy:
    """
    Policy which checks that a not-yet verified claim matches one of a defined set of claims.
    """

    acceptable_claims: Collection[dict[str, Any]]

    def __init__(self, acceptable_claims: Collection[dict[str, Any]]):
        self.acceptable_claims = acceptable_claims

    def __call__(self, unvalidated_claims: oidc.UnvalidatedClaims):
        if not any(self._claims_match(unvalidated_claims, c) for c in self.acceptable_claims):
            LOG.info(
                "Rejecting token since it has no acceptable claims",
                actual_claims=unvalidated_claims,
                acceptable_claims=self.acceptable_claims,
            )
            raise InvalidClaimsError("Token does not have any acceptable claims.")

    def _claims_match(self, unvalidated_claims: dict[str, Any], expected_claims: dict[str, Any]):
        for k, v in expected_claims.items():
            if k not in unvalidated_claims or unvalidated_claims[k] != v:
                return False
        return True


class ExpectedUnverifiedAudienceAndIssuerPolicy(ExpectedUnverifiedClaimsPolicy):
    """
    Policy which checks that the unverified "aud" and "iss" claims matches one of a set.
    """

    def __init__(self, allowed_audience_and_issuers: Collection[tuple[str, str]]):
        super().__init__([{"aud": aud, "iss": iss} for (aud, iss) in allowed_audience_and_issuers])


class ExpectedUnverifiedClaimsPresentPolicy:
    """
    Policy which checks that the not-yet verified claims are present.
    """

    expected_claims: set[str]

    def __init__(self, expected_claims: Collection[str]):
        self.expected_claims = {c for c in expected_claims}

    def __call__(self, unvalidated_claims: oidc.UnvalidatedClaims):
        if not all(c in unvalidated_claims for c in self.expected_claims):
            LOG.info(
                "Rejecting token since it is lacking some required claims.",
                actual_claims=unvalidated_claims,
                expected_claims=self.expected_claims,
            )
            raise InvalidClaimsError("Token is missing at least one required claim.")
