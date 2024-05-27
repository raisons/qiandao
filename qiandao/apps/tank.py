#!/usr/bin/env python

import httpx
from typing import ClassVar, Generic, TypeVar, Optional
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from qiandao.core.task import Task
from qiandao.core.useragents import iphone_tank

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    code: str
    description: str
    data: Optional[T] = None


class SignInfo(BaseModel):
    sign_in: bool
    continue_sign_days: int
    sign_point: int
    continue_point: int
    lucky_point: int
    remind_point: int

    model_config = ConfigDict(alias_generator=to_camel)


class TankTask(Task):
    name: ClassVar[str] = "坦克App"

    access_token: str

    def get_http_client(self):
        return httpx.Client(
            headers={
                "Accept": "application/json, text/plain, */*",
                "User-Agent": iphone_tank,
                "accessToken": self.access_token,
                "brand": "7",
                "terminal": "GW_APP_TANK",
                "brandCode": "CCT001",
                "enterpriseId": "CC01",
                "rs": "2",  # required
            },
            base_url="https://gw-h5-gateway.gwmapp-w.com"
        )

    def get_signin_status(self) -> SignInfo:
        url = "/app-api/api/v1.0/signIn/getUserSignInStatus"
        resp = self.client.get(url).json()
        resp = Response[SignInfo].model_validate(resp)

        return resp.data

    def signin(self) -> bool:
        url = "/app-api/api/v1.0/signIn/sign"
        payload = {
            "port": "HJ0002"
        }
        resp = self.client.post(url, data=payload).json()
        self.debug(resp)
        resp = Response[str].model_validate(resp)
        if resp.code == "000000":
            return True

        self.log(resp.description, level='warning')
        return False

    def process(self):
        self.signin()
        info = self.get_signin_status()
        self.notify("连续签到:%s, 剩余坦克币:%s" % (
            info.continue_sign_days, info.remind_point
        ))
