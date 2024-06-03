#!/usr/bin/env python
import inspect
from datetime import datetime
from celery import current_app as app
from task import buildin
from task.base import Task
from notify import get_notifications


def notify(msg_list):
    message = ""
    for i, msg in enumerate(msg_list):
        if not msg:
            continue
        message += msg["name"]
        message += ":\n"

        for _m in msg["msg"]:
            message += "\n".join(_m)

        if i < len(msg_list) - 1:
            message += "\n\n"

    if message == "":
        return
    now = datetime.now().strftime("%Y%m%d")

    for notification in get_notifications():
        notification.send(message, title=f"每日签到{now}")


@app.task
def run_tasks():
    tasks = []
    members = inspect.getmembers(buildin)
    for name, member in members:
        if inspect.isclass(member) and issubclass(member, Task):
            tasks.append(member)

    msg_list = []
    for task in tasks:
        task_msg = []
        for sub_task in task.new():
            sub_task()
            task_msg.append(sub_task.get_message())

        msg_list.append({
            "name": task.name,
            "msg": task_msg
        })

    notify(msg_list)
