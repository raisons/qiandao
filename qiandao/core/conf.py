#!/usr/bin/env python
import yaml
from typing import Optional, Any
from pydantic import BaseModel

from qiandao.core.notify import BarkNotification


class Settings(BaseModel):
    debug: bool
    notify: Optional[BarkNotification] = None
    logging: dict
    tasks: dict[str, dict[str, Any]] = {}
    schedule: Optional[dict[str, Any]] = None

    @property
    def enabled_tasks(self):
        for task_name, task_conf in self.tasks.items():
            if task_conf.get("enable", False):
                yield task_name, task_conf

    @classmethod
    def from_yaml(cls, file):
        with open(file, "r") as fp:
            conf = yaml.safe_load(fp)
        return cls.model_validate(conf)
