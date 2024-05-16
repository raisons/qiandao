#!/usr/bin/env python
import abc
import logging
import httpx
from typing import ClassVar, Optional, Any
from pydantic import BaseModel, ConfigDict, Field
from apscheduler.schedulers.base import BaseScheduler

from qiandao.core.notify import Notification


class Task(BaseModel):
    name: ClassVar[str] = None

    client: httpx.Client = Field(default=None, exclude=True, repr=False)
    schedule: Optional[dict[str, Any]] = None
    pusher: Optional[Notification] = None

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
        if self.pusher:
            return self.pusher.send(message, title=self.name)

    def pre_process(self):
        self.client = self.get_http_client()

    @abc.abstractmethod
    def process(self):
        pass

    def post_process(self):
        self.client.close()

    def __call__(self, *args, **kwargs):
        self.log(f"processing job: {self.name}", level="DEBUG")
        self.pre_process()
        self.process()
        self.post_process()

    @staticmethod
    def split_cookie(raw_cookie: str):
        """
        解析cookie字符串
        """
        cookies = {}
        for i in raw_cookie.strip().split(";"):
            k, v = i.strip().split("=", 1)
            cookies[k] = v
        return cookies
