class AuthenticationError(RuntimeError):
    "Base class for all errors raised by the authentication module."


class InvalidIssuerError(AuthenticationError):
    "The issuer claim in the JWT was not correctly formed."


class InvalidJWKSUrlError(AuthenticationError):
    "The JWKS URL in the OIDC discovery document was not correctly formed."


class InvalidOIDCDiscoveryDocumentError(AuthenticationError):
    "The OIDC discovery document was malformed."


class InvalidTokenError(AuthenticationError):
    "The token was malformed or could not be validated against the issuer public key."


class TransportError(AuthenticationError):
    "There was an error fetching a URL."


class InvalidClaimsError(AuthenticationError):
    "The claims in the token did not match policy."
