#!/usr/bin/env python
import sys
import inspect
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

from qiandao.core import Task
from qiandao.core.log import configure_logging


class Scheduler:

    def __init__(self):
        self._scheduler = BlockingScheduler()

    def scheduled_job(self, trigger, *args, **kwargs):
        def inner(_callable):
            if inspect.isclass(_callable) and issubclass(_callable, Task):
                _callable = _callable()

            self._scheduler.add_job(_callable, trigger, *args, **kwargs)
            return _callable

        return inner

    def crontab_job(
        self,
        expr: str = None,
        year=None,
        month=None,
        day=None,
        week=None,
        day_of_week=None,
        hour=None,
        minute=None,
        second=None,
        start_date=None,
        end_date=None,
        timezone=None
    ):
        if expr:
            trigger = CronTrigger.from_crontab(expr, timezone=timezone)
        else:
            trigger = CronTrigger(
                year=year,
                month=month,
                day=day,
                week=week,
                day_of_week=day_of_week,
                hour=hour,
                minute=minute,
                second=second,
                start_date=start_date,
                end_date=end_date
            )

        return self.scheduled_job(trigger)

    def interval_job(
        self,
        weeks=0,
        days=0,
        hours=0,
        minutes=0,
        seconds=0,
        start_date=None,
        end_date=None,
        timezone=None
    ):
        trigger = IntervalTrigger(
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            start_date=start_date,
            end_date=end_date,
            timezone=timezone
        )
        return self.scheduled_job(trigger)

    def disposable_job(self, run_date=None, timezone=None):
        trigger = DateTrigger(
            run_date=run_date, timezone=timezone
        )
        return self.scheduled_job(trigger)

    def start(self):
        configure_logging()
        try:
            self._scheduler.start()
        except KeyboardInterrupt:
            sys.exit()


scheduler = Scheduler()
