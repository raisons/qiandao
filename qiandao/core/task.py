#!/usr/bin/env python
import abc
import logging
import httpx
import datetime
from typing import ClassVar, Optional, Any
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, ValidationError
from apscheduler.schedulers.base import BaseScheduler

from qiandao.core.notify import Notification
from qiandao.core.utils import ErrorConverter


class TaskException(Exception):
    pass


class TaskContext(BaseModel):
    pass


class Task(BaseModel):
    """
    Task基础类
    """
    name: ClassVar[str] = None
    client: httpx.Client = Field(default=None, exclude=True, repr=False)
    context: TaskContext = Field(default=None, exclude=True, repr=False)
    pusher: Optional[Notification] = None

    # 可配置项
    enable: Optional[bool] = True
    schedule: Optional[dict[str, Any]] = None
    http_proxy: Optional[HttpUrl] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def register_job(self, scheduler: BaseScheduler):
        if self.schedule:
            scheduler.add_job(self, **self.schedule)

    def get_http_client(self, *args, **kwargs):
        return httpx.Client(*args, **kwargs)

    @property
    def logger(self):
        return logging.getLogger(self.__module__)

    def log(self, message, level: str = "INFO"):
        mapping = logging.getLevelNamesMapping()
        self.logger.log(mapping[level], message)

    def notify(self, message: str):
        self.log("%s: %s" % (self.name, message))
        now = datetime.datetime.now()
        now = now.strftime("%Y%m%d")
        message = f"{now}: {message}"
        if self.pusher:
            return self.pusher.send(message, title=self.name)

    def raise_exception(self, message):
        raise TaskException(message)

    def pre_process(self):
        self.client = self.get_http_client()

    @abc.abstractmethod
    def process(self):
        pass

    def post_process(self):
        self.client.close()

    def __call__(self, *args, **kwargs):
        self.log(f"processing job: {self.name}", level="DEBUG")
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
