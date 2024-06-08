import uuid
from django.db import models
from system.models import Proxies


def alias(field_name):
    def wrap(self):
        return self.short(field_name)

    wrap.short_description = field_name
    wrap.__name__ = field_name

    return wrap


class TaskModel(models.Model):
    name = models.CharField(max_length=64, verbose_name="名称")
    enable = models.BooleanField(verbose_name="启用", default=False)
    proxy = models.ForeignKey(
        Proxies,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="代理"
    )

    def __str__(self):
        return self.name

    def short(self, field_name, max_length=50):
        field = getattr(self, field_name)
        if len(field) > max_length:
            return field[:max_length] + " ..."

        return field

    class Meta:
        abstract = True


class V2ex(TaskModel):
    cookies = models.TextField()

    short_cookies = alias("cookies")

    class Meta:
        verbose_name = "V2EX配置"
        verbose_name_plural = "V2EX"


class ItHome(TaskModel):
    username = models.CharField(max_length=64, verbose_name="用户名")
    password = models.CharField(max_length=64, verbose_name="密码")

    class Meta:
        verbose_name = "IT之家配置"
        verbose_name_plural = "IT之家"


class MLoL(TaskModel):
    client_ticket = models.TextField(null=False)
    user_id = models.CharField(max_length=128)

    short_client_ticket = alias("client_ticket")

    class Meta:
        verbose_name = "掌上英雄联盟配置"
        verbose_name_plural = "掌上英雄联盟"


class Tank(TaskModel):
    access_token = models.TextField()
    refresh_token = models.TextField(default="")
    device_id = models.TextField(default="")

    short_access_token = alias("access_token")
    short_refresh_token = alias("refresh_token")

    class Meta:
        verbose_name = "坦克App配置"
        verbose_name_plural = "坦克App"


class LinuxDo(TaskModel):
    cookies = models.TextField()
    csrf_token = models.TextField()
    username = models.CharField(max_length=32, null=True, blank=True)

    short_cookies = alias("cookies")

    class Meta:
        verbose_name = "Linux.do配置"
        verbose_name_plural = "Linux.do"


class Alipan(TaskModel):
    refresh_token = models.TextField()

    class Meta:
        verbose_name = "阿里云盘配置"
        verbose_name_plural = "阿里云盘"
