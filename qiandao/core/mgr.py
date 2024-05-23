#!/usr/bin/env python
import logging.config
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

from qiandao.core.task import Task
from qiandao.core.conf import Settings

from qiandao.apps.test import TestTask
from qiandao.apps.v2ex import V2exTask
from qiandao.apps.it_home import ItHomeTask
from qiandao.apps.tank import TankTask

TASKS = {
    "test": TestTask,
    "v2ex": V2exTask,
    "it_home": ItHomeTask,
    "tank": TankTask,
}


class QianDao:

    def __init__(self, config: str):
        self.settings = Settings.from_yaml(config)
        self.tasks: list[tuple[type[Task], dict]] = []

    def configure_logging(self):
        logging.config.dictConfig(self.settings.logging)

    def configure_tasks(self):
        for task_name, task_conf in self.settings.enabled_tasks:
            task_class = TASKS.get(task_name, None)
            if task_class:
                self.tasks.append((task_class, task_conf))

    def _start_task(self):
        msg_list = []
        for task_class, conf in self.tasks:
            task = task_class(**conf)
            # task.ctx.pusher = self.settings.notify
            task()
            msg_list.append({
                "name": task.name,
                "msg": task.ctx.msg
            })

        self.notify(msg_list)

    def notify(self, msg_list):
        message = ""
        for i, msg in enumerate(msg_list):
            message += msg["name"]
            message += ":\n"
            message += "\n".join(msg["msg"])
            if i < len(msg_list) - 1:
                message += "\n\n"

        now = datetime.now().strftime("%Y%m%d")
        self.settings.notify.send(message, title=f"每日签到{now}")

    def run(self, scheduled: bool = False):
        self.configure_logging()
        self.configure_tasks()

        if scheduled:
            scheduler = BlockingScheduler()
            scheduler.add_job(
                self._start_task,
                name="qiandao",
                **self.settings.schedule
            )
            scheduler.print_jobs()
            scheduler.start()

        else:
            self._start_task()
