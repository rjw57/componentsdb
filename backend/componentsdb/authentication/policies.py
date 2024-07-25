from collections.abc import Collection

import structlog

from . import oidc
from .exceptions import InvalidClaimsError

LOG = structlog.get_logger()


class ExpectedUnverifiedClaimPolicy:
    """
    Policy which checks that a not-yet verified claim matches one of a defined set.
    """

    claim: str
    expected_values: Collection[str]

    def __init__(self, claim: str, expected_values: Collection[str]):
        self.claim = claim
        self.expected_values = expected_values

    def __call__(self, unvalidated_claims: oidc.UnvalidatedClaims):
        value = unvalidated_claims.get(self.claim)
        if value not in self.expected_values:
            LOG.info(
                f"Rejecting token with invalid {self.claim} claim",
                value=value,
                expected_values=self.expected_values,
            )
            raise InvalidClaimsError(f"'{self.claim}' claim does not match any expected value.")


class ExpectedUnverifiedIssuerPolicy(ExpectedUnverifiedClaimPolicy):
    """
    Policy which checks that the unverified "iss" claim matches one of a set of issuers.
    """

    def __init__(self, expected_issuers: Collection[str]):
        super().__init__("iss", expected_issuers)


class ExpectedUnverifiedAudiencePolicy(ExpectedUnverifiedClaimPolicy):
    """
    Policy which checks that the unverified "aud" claim matches one of a set of audiences.
    """

    def __init__(self, expected_audiences: Collection[str]):
        super().__init__("aud", expected_audiences)


class ExpectedUnverifiedSubjectPolicy(ExpectedUnverifiedClaimPolicy):
    """
    Policy which checks that the unverified "sub" claim matches one of a set of subjects.
    """

    def __init__(self, expected_subjects: Collection[str]):
        super().__init__("sub", expected_subjects)
