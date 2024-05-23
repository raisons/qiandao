#!/usr/bin/env python
import abc
import logging
import httpx
from functools import cached_property
from typing import ClassVar, Optional, Annotated
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    ValidationError,
    PrivateAttr
)

from qiandao.core.notify import Notification
from qiandao.core.utils import ErrorConverter

Configurable = Field(frozen=True)


class TaskException(Exception):
    pass


class TaskContext(BaseModel):
    client: httpx.Client = None
    pusher: Optional[Notification] = None
    msg: list = []

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Task(BaseModel):
    """
    Task基础类
    """
    name: ClassVar[str] = None

    # 可配置项
    enable: Annotated[bool, Configurable] = False
    http_proxy: Annotated[HttpUrl, Configurable] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    _context: TaskContext = PrivateAttr()

    @property
    def ctx(self):
        return self._context

    @property
    def client(self):
        return self.ctx.client

    @cached_property
    def logger(self):
        return logging.getLogger(self.__module__)

    def get_http_client(self):
        return httpx.Client()

    def notify(self, message: str):
        self.logger.info("%s: %s" % (self.name, message))
        self.ctx.msg.append(message)

    def pre_process(self):
        self._context = TaskContext(
            client=self.get_http_client()
        )

    @abc.abstractmethod
    def process(self):
        pass

    def post_process(self):
        self._context.client.close()

    def __call__(self, *args, **kwargs):
        self.logger.debug(f"processing job: {self.name}")
        try:
            self.pre_process()
            self.process()
            self.post_process()
        except ValidationError as e:
            self.logger.error(ErrorConverter(e))

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
