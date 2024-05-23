#!/usr/bin/env python
import httpx
from typing import Literal, Annotated
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    ConfigDict,
    AliasGenerator,
    field_validator,
)
from pydantic.alias_generators import to_camel

from .base import Notification

BarkTimeLevel = Literal["active", "timeSensitive", "passive"]


class BarkNotification(Notification, BaseModel):
    """
    https://bark.day.app/#/tutorial
    """
    # host
    hostname: Annotated[
        str,
        Field(default="api.day.app", exclude=True)
    ]
    # device
    device_id: Annotated[str, Field(exclude=True)]
    # 铃声
    sound: str = None
    # 是否保存消息
    is_archive: str = None
    # 自定义推送图标
    icon: HttpUrl = None
    # 分组
    group: str = None
    # 时效性通知
    level: BarkTimeLevel = None
    # 点击推送会跳转到这个url
    url: HttpUrl = None
    # 只复制
    copy_text: str = Field(None, alias="copy")
    # 角标数字
    badge: int = None
    # 自动复制推送内送到剪贴板
    auto_copy: str = None

    model_config = ConfigDict(alias_generator=AliasGenerator(
        serialization_alias=to_camel
    ))

    @field_validator("hostname", "device_id")
    def validate_non_empty(cls, v: str):
        assert v != ""
        return v

    def build_url(self):
        return f"https://{self.hostname}/{self.device_id}"

    @property
    def params(self):
        return self.model_dump(
            by_alias=True,
            exclude_none=True,
            exclude_defaults=True
        )

    def send(self, message: str, title: str = None):
        url = self.build_url()
        payload = self.params
        payload["title"] = title
        payload["body"] = message

        response = httpx.post(url, json=payload)

        if response.status_code != 200:
            raise RuntimeError

        data = response.json()
        if data["code"] != 200 and data["message"] != "success":
            raise RuntimeError(data["message"])

        return True
