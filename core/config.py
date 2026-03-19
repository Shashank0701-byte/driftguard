import os
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

CORE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CORE_DIR.parent


def _default_docker_socket() -> str:
    if os.name == "nt":
        return "npipe:////./pipe/docker_engine"
    return "unix:///var/run/docker.sock"


class Settings(BaseSettings):
    """Configuration for the application."""

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://driftguard:driftguard@localhost:5432/driftguard"
    redis_url: str = "redis://localhost:6379"
    docker_socket: str = _default_docker_socket()
    compose_file_path: str = str(PROJECT_ROOT / "docker-compose.yml")
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_key: str = Field(alias="DRIFTGUARD_API_KEY")
    polling_interval: int = Field(default=60, alias="POLL_INTERVAL_SECONDS")

    @model_validator(mode="after")
    def normalize_paths(self) -> "Settings":
        compose_path = Path(self.compose_file_path)
        if not compose_path.is_absolute():
            self.compose_file_path = str((PROJECT_ROOT / compose_path).resolve())

        if os.name == "nt" and self.docker_socket == "unix:///var/run/docker.sock":
            self.docker_socket = _default_docker_socket()

        return self


settings = Settings()
