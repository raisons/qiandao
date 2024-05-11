#!/usr/bin/env python
import httpx
from typing import Literal
from pydantic import BaseModel, HttpUrl

from qiandao.core.conf import settings

BarkTimeLevel = Literal["active", "timeSensitive", "passive"]


class BarkParams(BaseModel):
    # 铃声
    sound: str = None
    # 是否保存消息
    isArchive: str = None
    # 自定义推送图标
    icon: HttpUrl = None
    # 分组
    group: str = None
    # 时效性通知
    level: BarkTimeLevel = None
    # 点击推送会跳转到这个url
    url: HttpUrl = None
    # 只复制
    # copy: str = None
    # 角标数字
    badge: int = None
    # 自动复制推送内送到剪贴板
    autoCopy: str = None


class Bark(BaseModel):
    scheme: str = "https"
    host: str
    device: str
    params: BarkParams = None

    @property
    def url(self) -> str:
        return "%s://%s/%s" % (
            self.scheme,
            self.host,
            self.device
        )

    def notify(self, content, title=None):
        if title:
            url = f"{self.url}/{title}/{content}"
        else:
            url = f"{self.url}/{content}"

        if self.params:
            params = self.param.model_dump(exclude_none=True)
        else:
            params = None
        response = httpx.get(url, params=params)
        if response.status_code != 200:
            raise RuntimeError

        data = response.json()
        if data["code"] != 200 and data["message"] != "success":
            raise RuntimeError(data["message"])

        return True


bark = Bark(
    host=settings.BARK_HOSTNAME,
    device=settings.BARK_DEVICE,
)

pusher = bark

if __name__ == '__main__':
    p = BarkParams(sound="asdf")
    print(p.model_dump(exclude_none=True))
