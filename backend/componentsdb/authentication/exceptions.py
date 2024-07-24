class AuthenticationError(RuntimeError):
    "Base class for all errors raised by the authentication module."


class InvalidIssuer(AuthenticationError):
    "The issuer claim in the JWT was not correctly formed."


class InvalidJWKSUrl(AuthenticationError):
    "The JWKS URL in the OIDC discovery document was not correctly formed."


class InvalidOIDCDiscoveryDocument(AuthenticationError):
    "The OIDC discovery document was malformed."


class InvalidToken(AuthenticationError):
    "The token was malformed or could not be validated against the issuer public key."


class FetchError(AuthenticationError):
    "There was an error fetching a URL."
