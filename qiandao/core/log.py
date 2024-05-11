#!/usr/bin/env python
import os
import logging
import logging.config
import logging.handlers
from rich.logging import RichHandler

from qiandao.core.conf import settings


class Log:
    level: int = logging.INFO
    fmt: str = None
    handler: logging.Handler = None

    def __init__(self):
        self.handler.setLevel(self.level)
        self.handler.setFormatter(logging.Formatter(self.fmt))
        self.handler.addFilter(self.filter)

    def __getattr__(self, item):
        return getattr(self.handler, item)

    def filter(self, record: logging.LogRecord) -> bool:
        return True

    @classmethod
    def register_to(cls, logger):
        if settings.DEBUG:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        logger.addHandler(cls().handler)


class RichLog(Log):
    fmt = "%(message)s"
    level = logging.DEBUG
    handler = RichHandler(
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        show_path=False
    )

    def filter(self, record: logging.LogRecord) -> bool:
        return settings.DEBUG


class ConsoleLog(Log):
    fmt = "%(asctime)s | %(levelname)-7s | %(message)s"  # noqa
    level = logging.DEBUG
    handler = logging.StreamHandler()

    def filter(self, record: logging.LogRecord) -> bool:
        return True


class FileLog(Log):
    fmt = ("%(asctime)s | %(levelname)-7s | %(process)d | "  # noqa
           "%(message)s | %(filename)s:%(lineno)-3d")
    level = logging.INFO
    handler = logging.handlers.RotatingFileHandler(settings.log_file)

    def filter(self, record: logging.LogRecord) -> bool:
        return not settings.DEBUG


def configure_logging():
    logger = logging.getLogger("qiandao")
    RichLog.register_to(logger)
    # ConsoleLog.register_to(logger, debug)
    FileLog.register_to(logger)
    return logger


if __name__ == '__main__':
    l = configure_logging()
    l.info("asdf")
    l.debug("asdf")
    l.error("asdfasdf")
    l.warning("asdfasdf")
