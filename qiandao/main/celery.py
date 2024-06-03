#!/usr/bin/env python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')


class Config:
    timezone = "Asia/Shanghai"
    enable_utc = False
    # 保存任务执行返回结果保存到Redis
    # celery 配置 redis
    # result_backend = 'redis://127.0.0.1:6379/11'
    broker_url = os.getenv("CELERY_BROKER")
    broker_connection_retry_on_startup = True
    # CELERY_BEAT_REDIS_SCHEDULER_KEY = 'qupot:celery:beat:tasks'
    # or the actual content-type (MIME)
    accept_content = ['application/json']
    # or the actual content-type (MIME)
    result_accept_content = ['application/json']
    # 任务超时
    # task_time_limit = 3000
    # redis 连接超时时间
    # redis_socket_timeout = 60
    # 禁用默认日志
    # worker_hijack_root_logger = False
    worker_redirect_stdouts = False


app = Celery('qiandao')
app.config_from_object(Config)
app.autodiscover_tasks(related_name='tasks')
