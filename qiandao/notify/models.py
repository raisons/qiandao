#!/usr/bin/env python
from abc import abstractmethod
from django.db import models
from urllib.parse import urljoin
from functools import partial
import httpx

ServerUrlField = partial(
    models.URLField,
    verbose_name="服务器地址",
    help_text="https:// 或者 http:// 开头"
)


class Notification(models.Model):
    name = models.CharField(verbose_name="名称", max_length=32)
    enable = models.BooleanField(verbose_name="开启", default=False)

    @abstractmethod
    def send(self, message: str, title: str = None):
        pass

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self._meta.verbose_name}(name={self.name})"


class BarkNotification(Notification):
    LEVEL_CHOICES = (
        ("active", "系统会立即亮屏显示通知"),
        ("timeSensitive", "时效性通知，可在专注状态下显示通知"),
        ("passive", "仅将通知添加到通知列表，不会亮屏提醒"),
    )

    server = ServerUrlField(default="https://api.day.app")
    device_id = models.CharField(verbose_name="设备ID", max_length=64)

    level = models.CharField(
        verbose_name="推送中断级别",
        max_length=32,
        null=True,
        blank=True,
        choices=LEVEL_CHOICES,
        default="active"
    )

    badge = models.PositiveSmallIntegerField(
        verbose_name="角标",
        null=True,
        blank=True,
        help_text="推送角标，可以是任意数字"
    )
    sound = models.CharField(
        verbose_name="铃声",
        max_length=32,
        null=True,
        blank=True,
        help_text="可以为推送设置不同的铃声"
    )
    icon = models.URLField(
        verbose_name="图标",
        null=True,
        blank=True,
        help_text="为推送设置自定义图标，设置的图标将替换默认Bark图标。"
                  "图标会自动缓存在本机，相同的图标 URL 仅下载一次。"
    )
    group = models.CharField(
        verbose_name="群组",
        max_length=32,
        null=True,
        blank=True,
        help_text="对消息进行分组，推送将按group分组显示在通知中心中。"
                  "也可在历史消息列表中选择查看不同的群组。"
    )
    is_archive = models.CharField(
        verbose_name="是否保存",
        max_length=32,
        null=True,
        blank=True,
        help_text="传 1 保存推送，传其他的不保存推送，不传按APP内设置来决定是否保存。"
    )
    url = models.URLField(
        verbose_name="跳转链接",
        null=True,
        blank=True,
        help_text="点击推送时，跳转的URL ，支持URL Scheme 和 Universal Link"
    )

    class Meta:
        verbose_name = verbose_name_plural = "Bark"

    def send(self, message: str, title: str = None):
        url = urljoin(self.server, self.device_id)
        payload = {
            "title": title,
            "body": message,
            "sound": self.sound,
            "isArchive": self.is_archive,
            "icon": self.icon,
            "group": self.group,
            "level": self.level,
            "url": self.url,
            "badge": self.badge,
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        resp = httpx.post(url, json=payload).json()

        assert resp["code"] == 200


class ServerChanNotification(Notification):
    class Meta:
        verbose_name = verbose_name_plural = "server酱"


class PushDeerNotification(Notification):
    server = ServerUrlField(default="https://api2.pushdeer.com")
    push_key = models.CharField(verbose_name="PushKey", max_length=128)

    class Meta:
        verbose_name = verbose_name_plural = "PushDeer"

    def send(self, message: str, title: str = None):
        url = urljoin(self.server, "/message/push")
        payload = {
            "pushkey": self.push_key,
            "text": message,
            "type": "markdown",
        }
        httpx.post(url, json=payload)
