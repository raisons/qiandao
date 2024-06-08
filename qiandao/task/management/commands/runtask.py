#!/usr/bin/env python
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "run task"

    def add_arguments(self, parser):
        parser.add_argument(
            dest='task_class_name',
            nargs=1,
            help="task class name"
        )

    def handle(self, *args, **options):
        task_class_name = options["task_class_name"][0]
        print(task_class_name)

        import task.buildin as buildin

        task_class = getattr(buildin, task_class_name, None)
        if not task_class:
            raise RuntimeError(f"Not found task class: {task_class_name}")

        for task in task_class.new():
            task()
