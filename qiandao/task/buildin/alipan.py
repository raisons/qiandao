#!/usr/bin/env python
import uuid

import httpx
import dataclasses
import hashlib
import ecdsa as ec
from functools import cached_property
from random import randint
from datetime import datetime
from typing import ClassVar, Generic, TypeVar
from pydantic import BaseModel as Schema, model_validator, ConfigDict
from pydantic import PrivateAttr
from pydantic.alias_generators import to_camel

from task.base import Task
from task.models import Alipan
from task.useragents import safari, alipan_app

T = TypeVar('T')


class Response(Schema, Generic[T]):
    success: bool
    code: int | str | None
    message: str | None
    result: T | None

    @model_validator(mode="after")
    def validate_success(self):
        if not self.success:
            raise ValueError(self.message)

        return self


class Token(Schema):
    access_token: str
    refresh_token: str
    nick_name: str
    user_id: str


class SignReward(Schema):
    name: str
    remind: str
    status: str


class SignInInfo(Schema):
    day: str
    date: str | None
    status: str
    rewards: list[SignReward]


class SignResult(Schema):
    month: str
    sign_in_count: int
    sign_in_infos: list[SignInInfo]

    def today(self):
        now = datetime.now().day
        for info in self.sign_in_infos:
            if info.date and int(info.date) == now:
                return info

        return None

    model_config = ConfigDict(alias_generator=to_camel)


class Signer(Schema):
    app_id: str
    user_id: str

    _device_id: str = PrivateAttr(None)
    _nonce: int = PrivateAttr(default=0)
    _sign_key: ec.SigningKey = PrivateAttr(None)
    _verify_key: ec.VerifyingKey = PrivateAttr(None)

    @property
    def device_id(self) -> str:
        if not self._device_id:
            self._device_id = str(uuid.uuid4())
        return self._device_id

    @property
    def sign_key(self) -> ec.SigningKey:
        if not self._sign_key:
            self._sign_key = ec.SigningKey.from_secret_exponent(
                secexp=randint(1, 2 ** 256 - 1),
                curve=ec.SECP256k1
            )
        return self._sign_key

    @property
    def verify_key(self) -> ec.VerifyingKey:
        if not self._verify_key:
            self._verify_key = self.sign_key.get_verifying_key()
        return self._verify_key

    @property
    def private_key(self) -> str:
        return self.sign_key.to_string().hex()

    @property
    def public_key(self) -> str:
        return "04" + self.verify_key.to_string().hex()

    @cached_property
    def signature(self) -> str:
        msg = f"{self.app_id}:{self.device_id}:{self.user_id}:{self._nonce}"

        sign = self.sign_key.sign(
            msg.encode('utf-8'),
            entropy=None,
            hashfunc=hashlib.sha256
        )
        return sign.hex() + "01"


class AlipanTask(Task):
    name: ClassVar[str] = "阿里云盘"

    app_id: ClassVar[str] = "25dzX3vbYqktVxyX"
    version: ClassVar[str] = "v5.8.1"

    model: Alipan

    def create_signature(self, user_id) -> Signer:
        signer = Signer(user_id=user_id, app_id=self.app_id)

        # 更新header
        self.client.headers.update({
            "User-Agent": alipan_app,
            "X-Canary": f"client=iOS,app=adrive,version={self.version}",
            "x-device-id": signer.device_id,
            "x-signature": signer.signature,
        })

        self.create_session(signer.public_key)
        return signer

    def create_session(self, public_key: str):
        url = "https://api.aliyundrive.com/users/v1/users/device/create_session"
        payload = {
            "deviceName": "iPhone",
            "modelName": "iPhone13,4",
            "pubKey": public_key,
        }
        resp = self.client.post(url, json=payload).json()
        self.debug(resp)
        Response.model_validate(resp)

    def refresh_token(self) -> Token:
        url = 'https://auth.aliyundrive.com/v2/account/token'
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self.model.refresh_token
        }

        resp = httpx.post(url, json=payload).json()
        resp = Token.model_validate(resp)

        # 更新refresh_token
        self.model.refresh_token = resp.refresh_token
        self.model.save()

        self.client.headers = {
            "Authorization": f"Bearer {resp.access_token}"
        }

        return resp

    def sign_rewards(self, sign_in_day: int):
        url = "https://member.aliyundrive.com/v1/activity/sign_in_reward"
        payload = {"signInDay": sign_in_day}
        params = {"_rx-s": "mobile"}
        resp = self.client.post(url, json=payload).json()
        self.debug(resp)
        Response.model_validate(resp)

    def sign_in(self) -> SignResult | None:
        url = "https://member.aliyundrive.com/v2/activity/sign_in_list"
        payload = {'isReward': False}
        resp = self.client.post(url=url, json=payload).json()

        resp = Response[SignResult].model_validate(resp)

        info = resp.result.today()

        if info.status == "normal":
            # 签到成功, 领取奖励 Todo
            # self.sign_rewards(resp.result.sign_in_count)
            return resp.result

        return None

    def process(self):
        token = self.refresh_token()
        # self.create_signature(token.user_id)

        result = self.sign_in()
        if result:
            self.notify(f"签到成功: 本月累计签到{result.sign_in_count}天")

        else:
            self.notify(f"签到失败")
