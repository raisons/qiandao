#!/usr/bin/env python
import click
from qiandao.core.conf import Settings
from apscheduler.schedulers.blocking import BlockingScheduler


@click.command()
@click.option("-c", "--config", default="qiandao.yaml")
@click.option("--scheduled", default=False, is_flag=True)
def main(config: str, scheduled: bool):
    settings = Settings.from_yaml(config)
    settings.configure_notifications()
    settings.configure_logging()

    if scheduled:
        scheduler = BlockingScheduler()
        for task_name, task in settings.enabled_tasks:
            if task.schedule:
                scheduler.add_job(task, name=task_name, **task.schedule)

        scheduler.print_jobs()
        scheduler.start()

    else:
        for task_name, task in settings.enabled_tasks:
            task()


if __name__ == "__main__":
    main()
