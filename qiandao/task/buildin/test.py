#!/usr/bin/env python
from typing import ClassVar
from task.base import Task
from task.models import MLoL


class TestTask(Task):
    name: ClassVar[str] = "TestTask"
    model: MLoL

    def process(self):
        self.notify("测试成功")
        # self.logger.debug("测试成功")
