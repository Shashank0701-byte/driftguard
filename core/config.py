from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration for the application."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://driftguard:driftguard@localhost:5432/driftguard"
    redis_url: str = "redis://localhost:6379"
    docker_socket: str = "unix:///var/run/docker.sock"
    compose_file_path: str = "./docker-compose.yml"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    polling_interval: int = Field(default=60, alias="POLL_INTERVAL_SECONDS")


settings = Settings()
