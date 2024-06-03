#!/usr/bin/env python

from typing import ClassVar, Generic, TypeVar

import httpx
from pydantic import BaseModel, HttpUrl

from task.base import Task
from task.useragents import m_lol
from task.models import MLoL

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    result: int
    msg: str
    err_msg: str
    data: T = None


class CommunityInfo(BaseModel):
    exp: int
    level: int
    mengbi: int
    exp_percent: int
    result: int
    err_msg: str


class CommunityTask(BaseModel):
    name: str
    reward: str
    icon_url: HttpUrl
    status: int
    jump_url: str
    total_day_count: int
    sign_day_count: int
    action_title: str
    task_id: int
    sub_task_list: list["CommunityTask"] = None


class CommunityTaskList(BaseModel):
    task_list: list[CommunityTask]
    result: int
    err_msg: str


class ClientTickerInfo(BaseModel):
    ct: str
    main_account_type: int
    result: int
    refresh_ct_span: int
    openid: str
    user_id: str
    is_timeout: int
    is_new_user: int
    refresh_wt_span: int
    errmsg: str
    wt: str
    uin: int
    expires: int
    login_uuid: str


class BindInfo(BaseModel):
    uin: str
    openid: str
    uuid: str
    nickName: str
    sex: str
    selfUuid: str
    type: int
    thirdType: int
    iconUrl: str
    isRegisterUin: int
    isVerification: int
    eventTime: str
    isSyncAttention: int
    deviceId: str


class RefreshClientTicket(BaseModel):
    ct_info: ClientTickerInfo
    bind_info: list[BindInfo]

    @property
    def bound(self) -> BindInfo | None:
        for info in self.bind_info:
            if info.uuid == self.ct_info.user_id:
                return info

        return None


class ThirdToken(BaseModel):
    access_token: str
    expired: int
    time_interval: int


class MLoLTask(Task):
    name: ClassVar[str] = "掌上英雄联盟"

    model: MLoL

    def get_http_client(self):
        return httpx.Client(
            headers={
                "User-Agent": m_lol,
            },
        )

    def refresh_client_ticket(self) -> RefreshClientTicket:
        url = "https://mlol.qt.qq.com/go/auth/refresh_client_ticket"
        payload = {
            "ct": self.model.client_ticket,
            "config_params": {
                "lang_type": 0
            },
            "user_id": self.model.user_id,
            "local_is_new_user": 0
        }

        resp = self.client.post(url, json=payload).json()

        resp = Response[RefreshClientTicket].model_validate(resp)
        return resp.data

    def refresh_third_token(self, openid, cookies) -> str:
        url = "https://mlol.qt.qq.com/go/auth/refresh_third_token"
        payload = {
            "type": "qc",
            "openid": openid,
            "uuid": self.model.user_id
        }
        resp = self.client.post(url, json=payload, cookies=cookies).json()

        resp = Response[ThirdToken].model_validate(resp)
        return resp.data.access_token

    def get_cookies(self, openid, uin, tid):
        return {
            "openid": openid,
            "appid": "100543809",
            "acctype": "qc",
            "uid": f"o{uin}",
            "userId": self.model.user_id,
            "tid": tid,
            "clientType": "10",
            "accountType": "5",
        }

    def get_community_info(self) -> CommunityInfo:
        url = "https://mlol.qt.qq.com/go/user_profile/get_community_info"
        params = {
            "plat": "ios",
            "version": 1000,
        }
        payload = {
            "client_type": 10
        }
        resp = self.client.post(url, params=params, json=payload).json()
        resp = Response[CommunityInfo].model_validate(resp)
        return resp.data

    def get_community_task(self) -> list[CommunityTask]:
        url = "https://mlol.qt.qq.com/go/user_profile/get_community_task"
        params = {
            "plat": "ios",
            "version": 1000,
        }
        payload = {
            "client_type": 10
        }
        resp = self.client.post(url, params=params, json=payload).json()
        resp = Response[CommunityTaskList].model_validate(resp)
        return resp.data.task_list

    def signin(self):
        url = "https://mlol.qt.qq.com/go/user_profile/report_task_action"
        params = {
            "plat": "ios",
            "version": 1000,
        }
        payload = {
            "task_id": 1,
            "client_type": 10
        }
        resp = self.client.post(url, params=params, json=payload).json()
        self.debug(resp)

    def pre_process(self):
        super().pre_process()
        ct = self.refresh_client_ticket()

        cookies = self.get_cookies(
            openid=ct.bound.openid,
            uin=ct.bound.uin,
            tid=ct.ct_info.wt
        )
        access_token = self.refresh_third_token(
            openid=ct.bound.openid,
            cookies=cookies
        )
        cookies["access_token"] = access_token

        self.client.cookies = cookies

    def process(self):
        self.signin()
        into = self.get_community_info()
        self.notify(f"经验值:{into.exp}, 等级:{into.level}, 萌币:{into.mengbi}")
