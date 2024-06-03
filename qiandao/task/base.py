#!/usr/bin/env python
import abc
import logging
import httpx
from functools import cached_property
from typing import ClassVar, Optional, Annotated, Literal, cast
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    ValidationError,
    PrivateAttr
)

from .utils import ErrorConverter
from .models import TaskModel

LOG_LEVEL = Literal["info", "debug", "warning", "error", "exception"]


class Task(BaseModel):
    """
    Task基础类
    """
    name: ClassVar[str] = None

    model: TaskModel

    _client: httpx.Client = PrivateAttr()
    _message: list[str] = PrivateAttr(default_factory=list)

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    @classmethod
    def new(cls):
        model_field_info = cls.model_fields["model"]
        model_cls = model_field_info.annotation

        for obj in model_cls.objects.all():
            yield cls(model=obj)

    @property
    def client(self):
        return self._client

    @cached_property
    def logger(self):
        return logging.getLogger("qiandao")

    def get_http_client(self):
        return httpx.Client(
            proxies=self.get_http_proxies()
        )

    def get_http_proxies(self) -> dict[str, str] | None:
        if self.model.proxy:
            proxies = self.model.proxy.as_dict()

            self.debug(proxies)
            return proxies

        return None

    def log(self, message, level: LOG_LEVEL = "info"):
        getattr(self.logger, level)("%s: %s" % (self.name, message))

    def debug(self, message):
        self.log(message, level="debug")

    def notify(self, message: str):
        self.log(message)
        self._message.append(message)

    def get_message(self):
        return self._message

    def pre_process(self):
        self._client = self.get_http_client()

    @abc.abstractmethod
    def process(self):
        pass

    def post_process(self):
        self._client.close()

    def __call__(self, *args, **kwargs):
        self.debug(f"processing task")
        try:
            self.pre_process()
            self.process()
            self.post_process()
        except ValidationError as e:
            convert = ErrorConverter(e)
            self.log(convert, level="exception")
            self.notify(str(convert))
        except Exception as e:
            self.log(e, level="exception")
            self.notify(str(e))

    @staticmethod
    def split_cookie(raw_cookie: str) -> dict[str, str]:
        """
        解析cookie字符串
        """
        cookies = {}
        for i in raw_cookie.strip().split(";"):
            k, v = i.strip().split("=", 1)
            cookies[k] = v
        return cookies
