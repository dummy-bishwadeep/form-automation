from pydantic import Field
from pydantic_settings import BaseSettings

from scripts.config.app_configurations import Service, Path, LoggingDetails


class _Services(BaseSettings):
    HOST: str = Field(default=Service.SERVICE_HOST, env="service_host")
    PORT: int = Field(default=int(Service.SERVICE_PORT), env="service_port")
    PROJECT_NAME: str = Field(default=Service.PROJECT_NAME, env="project_name")
    ENABLE_CORS: bool = True
    CORS_URLS: list = ["*.ilens.io"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["GET", "POST"]
    CORS_ALLOW_HEADERS: list = ["*"]
    LOG_LEVEL: str = LoggingDetails.LOG_LEVEL
    BACKUP_COUNT: int = LoggingDetails.BACKUP_COUNT
    MAX_BYTES: int = LoggingDetails.MAX_BYTES
    ENABLE_FILE_LOGGING: bool = True
    ENABLE_BACKUP_STORING: bool = Field(default=False, env="enable_backup")
    WORKERS: int = Field(default=1, env="workers")


class _BasePathConf(BaseSettings):
    BASE_PATH: str = "/"


class _PathConf(BaseSettings):
    LOG_PATH: str = LoggingDetails.LOG_PATH
    CONFIG_PATH: str = Path.CONFIG_PATH


Services = _Services()
PathConf = _PathConf()

__all__ = [
    "Services",
    "PathConf",
]
