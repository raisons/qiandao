#!/usr/bin/env python
import re
import httpx
from typing import ClassVar
from lxml import html

from task.base import Task
from task.useragents import safari
from task.models import V2ex


class V2exTask(Task):
    """
    V2EX 领取每日铜币
    """
    name: ClassVar[str] = "V2EX"

    model: V2ex

    def get_http_client(self):
        return httpx.Client(
            headers={
                "Referer": "https://www.v2ex.com/",
                "User-Agent": safari
            },
            cookies=self.split_cookie(self.model.cookies),
            proxies=self.get_http_proxies()
        )

    def query_balance(self):
        """
        查询账户余额
        """
        response = self.client.get("https://www.v2ex.com/balance")
        doc = html.fromstring(response.text)
        trs = doc.cssselect("table.data tr")
        tds = trs[1].cssselect("td")
        return tds[3].text_content()

    def check_in(self, once: str):
        # 无内容返回
        self.client.get(
            f"https://www.v2ex.com/mission/daily/redeem?once={once}"
        )

    def process(self):
        response = self.client.get(
            "https://www.v2ex.com/mission/daily"
        )

        if "你要查看的页面需要先登录" in response.text:
            self.notify("登录失败，Cookie 可能已经失效")
            return

        elif "每日登录奖励已领取" in response.text:
            msg = ("每日登录奖励已领取，" +
                   re.search(r"已连续登录 \d+ 天", response.text)[0])
            self.notify(msg)
            return

        # 获取once
        match = re.search(r"once=(\d+)", response.text)
        if not match:
            self.notify("未获取到once")
            return

        try:
            once = match.group(1)
            # 领取铜币
            self.check_in(once)
            # self.notify("")
            coins = self.query_balance()
            self.notify(f"领取成功:账户余额{coins}")

        except IndexError:
            pass
