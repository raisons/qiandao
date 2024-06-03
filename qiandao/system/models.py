from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Meta:
        abstract = False
        verbose_name = verbose_name_plural = "用户管理"


class Proxies(models.Model):
    name = models.CharField(max_length=64, verbose_name="名称")
    http = models.URLField(verbose_name="http地址")
    https = models.URLField(verbose_name="https地址")

    class Meta:
        verbose_name = verbose_name_plural = "代理"

    def as_dict(self):
        return {
            "http://": self.http,
            "https://": self.https
        }
