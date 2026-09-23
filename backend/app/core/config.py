from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"

    database_url: str
    test_database_url: str = "postgresql+asyncpg://bidpilot:bidpilot@localhost:5432/bidpilot_test"

    redis_url: str = "redis://localhost:6379/0"

    cors_origins: str = "http://localhost:5173"
    frontend_base_url: str = "http://localhost:5173"

    # Phase 0.3 — not required for the app to boot before then.
    jwt_secret_key: str | None = None
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 30

    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_use_tls: bool = True

    google_oauth_client_id: str | None = None
    google_oauth_client_secret: str | None = None

    # Phase 1.1
    s3_endpoint_url: str = "http://localhost:9000"
    s3_bucket: str = "bidpilot-dev"
    aws_access_key_id: str = "minioadmin"
    aws_secret_access_key: str = "minioadmin"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
