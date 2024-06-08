#!/usr/bin/env python

import httpx
import json
import hashlib
import string
import secrets
import time
from urllib.parse import quote_plus
from typing import ClassVar, Generic, TypeVar, Optional
from pydantic import BaseModel, ConfigDict, model_validator
from pydantic.alias_generators import to_camel

from task.base import Task
from task.useragents import iphone_tank
from task.models import Tank

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    valid_code: ClassVar[list[str]] = ["651028", ]

    code: str
    description: str
    data: Optional[T] = None

    @model_validator(mode="after")
    def validate_code(self):
        if self.code != "000000" and self.code not in self.valid_code:
            raise ValueError(f"{self.code}: {self.description}")
        return self


class SignInfo(BaseModel):
    sign_in: bool
    continue_sign_days: int
    sign_point: int
    continue_point: int
    lucky_point: int
    remind_point: int

    model_config = ConfigDict(alias_generator=to_camel)


class RefreshToken(BaseModel):
    access_token: str
    refresh_token: str

    model_config = ConfigDict(alias_generator=to_camel)


class TankTask(Task):
    name: ClassVar[str] = "坦克App"
    app_key: ClassVar[str] = "7736975579"
    app_secret: ClassVar[str] = "8a23355d9f6a3a41deaf37a628645c62"

    model: Tank

    def get_http_client(self):
        return httpx.Client(
            headers={
                "Accept": "application/json, text/plain, */*",
                "User-Agent": iphone_tank,
                # "accessToken": self.model.access_token,
                "brand": "7",
                "terminal": "GW_APP_TANK",
                "brandCode": "CCT001",
                "enterpriseId": "CC01",
                "rs": "2",  # required
            },
        )

    def get_signature(
        self,
        method: str,
        path: str,
        nonce: str,
        timestamp: str,
        payload: str,
    ) -> str:
        """"
        核心签名逻辑
        """
        s = (
            f"{method}{path}"
            f"bt-auth-appkey:{self.app_key}"  # noqa
            f"bt-auth-nonce:{nonce}"
            f"bt-auth-timestamp:{timestamp}"
            f"{payload}"
            f"{self.app_secret}"
        )

        s = quote_plus(s)
        s = hashlib.sha256(s.encode()).hexdigest()
        return s

    def refresh_token(self) -> RefreshToken:
        path = "/app-api/api/v1.0/userAuth/refreshToken"
        url = f"https://gw-app.beantechyun.com{path}"
        payload = {
            "accessToken": self.model.access_token,
            "refreshToken": self.model.refresh_token,
            "deviceId": self.model.device_id,
        }

        # 生成签名
        chars = string.digits + string.ascii_lowercase
        nonce = "".join(
            secrets.choice(chars) for i in range(16)
        )
        timestamp = str(int(time.time() * 1000))
        payload_json = "json=" + json.dumps(payload)
        payload_json = payload_json.replace(" ", "")

        signature = self.get_signature(
            "POST",
            path,
            nonce,
            timestamp,
            payload_json
        )

        headers = {
            "bt-auth-sign": signature,
            "bt-auth-timestamp": timestamp,
            "bt-auth-nonce": nonce,
            "bt-auth-appkey": self.app_key,  # noqa
        }
        resp = self.client.post(url, json=payload, headers=headers).json()
        resp = Response[RefreshToken].model_validate(resp)

        # 更新数据库
        self.model.refresh_token = resp.data.refresh_token
        self.model.access_token = resp.data.access_token
        self.model.save()

        return resp.data

    def get_signin_status(self) -> SignInfo:
        url = ("https://gw-h5-gateway.gwmapp-w.com"
               "/app-api/api/v1.0/signIn/getUserSignInStatus")
        resp = self.client.get(url, headers={
            "accessToken": self.model.access_token
        }).json()
        resp = Response[SignInfo].model_validate(resp)

        return resp.data

    def signin(self) -> bool:
        url = "https://gw-h5-gateway.gwmapp-w.com/app-api/api/v1.0/signIn/sign"
        payload = {
            "port": "HJ0002"
        }
        resp = self.client.post(url, data=payload, headers={
            "accessToken": self.model.access_token
        }).json()
        self.debug(resp)
        resp = Response[str].model_validate(resp)
        if resp.code == "000000":
            return True

        self.log(resp.description, level='warning')
        return False

    def process(self):
        self.refresh_token()
        self.signin()
        info = self.get_signin_status()
        self.notify("连续签到:%s, 剩余坦克币:%s" % (
            info.continue_sign_days, info.remind_point
        ))
