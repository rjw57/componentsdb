from componentsdb.authentication import oidc


def test_oidc_token_issuer(oidc_token: str, jwt_issuer: str):
    assert oidc.unvalidated_issuer_from_token(oidc_token) == jwt_issuer
