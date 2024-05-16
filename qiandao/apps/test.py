#!/usr/bin/env python
from typing import ClassVar
from qiandao.core.task import Task


class TestTask(Task):
    name: ClassVar[str] = "TestTask"

    def process(self):
        # self.notify("测试成功")
        self.log("测试成功")
