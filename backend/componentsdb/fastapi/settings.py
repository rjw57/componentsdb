from pydantic import Field
from pydantic_settings import BaseSettings

from ..auth import FederatedIdentityProvider


class Settings(BaseSettings):
    sqlalchemy_db_url: str
    access_token_lifetime: int = 3600
    federated_identity_providers: dict[str, FederatedIdentityProvider] = Field(
        default_factory=dict
    )


def load_settings() -> Settings:
    return Settings()
