from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class _Services(BaseSettings):
    HOST: str = Field(default="127.0.0.1", env="service_host")
    PORT: int = Field(default=8080, env="service_port")
    PROJECT_NAME: str = Field(default="UT-Automation", env="project_name")
    ENABLE_CORS: bool = True
    CORS_URLS: list = ["*.ilens.io"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["GET", "POST"]
    CORS_ALLOW_HEADERS: list = ["*"]
    LOG_LEVEL: str
    BACKUP_COUNT: int
    MAX_BYTES: int
    ENABLE_FILE_LOGGING: bool = True
    ENABLE_BACKUP_STORING: bool = Field(default=False, env="enable_backup")
    WORKERS: int = Field(default=1, env="workers")


class _BasePathConf(BaseSettings):
    BASE_PATH: str = "/"


class _PathConf(BaseSettings):
    LOG_PATH: str
    CONFIG_PATH: str


Services = _Services()
PathConf = _PathConf()

__all__ = [
    "Services",
    "PathConf",
]
