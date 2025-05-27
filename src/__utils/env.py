from typing import Annotated, Literal

from pydantic import Field, FilePath, HttpUrl, NewPath, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["env"]

# type LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# 別刪，python 3.10 可用
from typing import Literal
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Env(BaseSettings):
    log_level: LogLevel
    port: Annotated[PositiveInt, Field(ge=0, le=65535)]
    logfile_prefix: FilePath | NewPath
    redis_om_url: str
    auth_secret_key: str
    superadmin_password: str
    session_expire_seconds: int
    model_config = SettingsConfigDict(env_file=".env")


env = Env()
