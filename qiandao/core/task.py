#!/usr/bin/env python
import abc
import logging
import httpx

from qiandao.core.notifications import bark
from qiandao.core.conf import settings

logger = logging.getLogger(__name__)


class Task:
    name: str = None
    pusher = bark
    settings = settings

    def __init__(self):
        self.client = self.get_http_client()

    def get_http_client(self):
        return httpx.Client()

    def log(self, message, level: str = "INFO"):
        mapping = logging.getLevelNamesMapping()
        logger.log(mapping[level], message)

    def notify(self, message: str):
        self.log("%s: %s" % (self.name, message))
        return self.pusher.notify(message, title=self.name)

    def pre_process(self):
        pass

    @abc.abstractmethod
    def process(self):
        pass

    def post_process(self):
        pass

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
