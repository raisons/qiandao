#!/usr/bin/env python
from datetime import datetime
from qiandao.core import Task, scheduler


# @schedule.scheduler.interval_job(seconds=3)
@scheduler.disposable_job()
class Test(Task):
    name = "TestTask"

    def process(self):
        # self.notify("测试成功")
        self.log("测试成功")
