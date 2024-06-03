#!/usr/bin/env python
import multiprocessing
import gevent.monkey

gevent.monkey.patch_all()
bind = "0.0.0.0:6677"
workers = multiprocessing.cpu_count()
worker_class = "gevent"

access_log_format = '%({x-forwarded-for}i)s %(h)s %(l)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s"'
accesslog = "storages/logs/gunicorn.access.log"
errorlog = "storages/logs/gunicorn.error.log"

forwarded_allow_ips = "*"
