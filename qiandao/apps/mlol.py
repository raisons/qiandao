#!/usr/bin/env python

from typing import ClassVar, Generic, TypeVar

import httpx
from pydantic import BaseModel, HttpUrl

from qiandao.core.task import Task
from qiandao.core.useragents import m_lol

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


class MLoLTask(Task):
    name: ClassVar[str] = "掌上英雄联盟"

    cookies: str

    def get_http_client(self):
        return httpx.Client(
            headers={
                "User-Agent": m_lol,
            },
            cookies=self.split_cookie(self.cookies)
        )

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

    def process(self):
        self.signin()
        into = self.get_community_info()
        self.notify(f"经验值:{into.exp}, 等级:{into.level}, 萌币:{into.mengbi}")
