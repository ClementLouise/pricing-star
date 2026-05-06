from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    # Auth0
    auth0_domain: str
    auth0_audience: str = "https://api.pricingstar.io"
    auth0_client_id: str  # M2M client ID
    auth0_client_secret: str  # M2M client secret

    # Internal webhook security
    webhook_secret: str

    # Sentry (optional)
    sentry_dsn: str = ""

    # CORS
    allowed_origins: list[str] = ["http://localhost:5173"]

    # Trial limits
    trial_max_assets: int = 5
    trial_max_scenarios_per_asset: int = 3
    trial_max_users: int = 3

    @property
    def auth0_jwks_url(self) -> str:
        return f"https://{self.auth0_domain}/.well-known/jwks.json"

    @property
    def auth0_issuer(self) -> str:
        return f"https://{self.auth0_domain}/"


settings = Settings()  # type: ignore[call-arg]
