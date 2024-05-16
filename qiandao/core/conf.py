#!/usr/bin/env python
import yaml
import logging.config
from rich import print
from pydantic import BaseModel

from qiandao.core.notify import BarkNotification
from qiandao.apps.test import TestTask
from qiandao.apps.v2ex import V2exTask
from qiandao.apps.linux_do import LinuxDoTask
from qiandao.apps.it_home import ItHomeTask


class Tasks(BaseModel):
    v2ex: V2exTask = None
    test: TestTask = None
    linux_do: LinuxDoTask = None
    it_home: ItHomeTask = None


class Settings(BaseModel):
    debug: bool
    notify: BarkNotification = None
    logging: dict
    tasks: Tasks

    @property
    def enabled_tasks(self):
        for task_name, task in self.tasks:
            if task and task.enable:
                yield task_name, task

    @classmethod
    def from_yaml(cls, file):
        with open(file, "r") as fp:
            conf = yaml.safe_load(fp)
        return cls.model_validate(conf)

    def configure_notifications(self):
        for task_name, task in self.enabled_tasks:
            task.pusher = self.notify

    def configure_logging(self):
        logging.config.dictConfig(self.logging)


if __name__ == '__main__':
    settings = Settings.from_yaml("qiandao.yaml")
    settings.configure_notifications()
    settings.configure_logging()
    # print(settings.tasks.test)

    for i in settings.tasks:
        print(i)

    print(settings.notify)

    print(settings)
