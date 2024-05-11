#!/usr/bin/env python
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    QIANDAO_DEBUG: bool = False  # noqa
    LOG_DIR: str = "."
    LOG_NAME: str = "qiandao.log"

    BARK_DEVICE: str
    BARK_HOSTNAME: str = "api.day.app"

    V2EX_COOKIES: str
    LINUXDO_COOKIES: str  # noqa
    LINUXDO_CSRF_TOKEN: str  # noqa

    @property
    def log_file(self):
        return Path(self.LOG_DIR).joinpath(self.LOG_NAME)

    @property
    def DEBUG(self):
        return self.QIANDAO_DEBUG

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
