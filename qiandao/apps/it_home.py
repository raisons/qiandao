#!/usr/bin/env python

import httpx
import re
import datetime
import binascii
from typing import ClassVar
from pydantic import BaseModel
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from qiandao.core.task import Task
from qiandao.core.useragents import ithome

STRING_LIST = (
    "hd7%b4f8p9)*fd4h5l6|)123/*-+!#$@%^*()_+?>?njidfds"
    "[]rfbcvnb3rz/ird|opqqyh487874515/%90hggigadfihklh"
    "kopjj`b3hsdfdsf84215456fi15451%q(#@Fzd795hn^Ccl$v"
    "K^L%#w$^yr%ETvX#0TaPSRm5)OeG)^fQnn6^%^UTtJI#3EZ@p"
    "6^Rf$^!O$(jnkOiBjn3#inhOQQ!aTX8R)9O%#o3zCVxo3tLyV"
    "orwYwA^$%^b9Yy$opSEAOOlFBsS^5d^HoF%tJ$dx%3)^q^c^$"
    "al%b4I)QHq^#^AlcK^KZFYf81#bL$n@$%j^H(%m^ "
)


# qiandaocode = [0, 1, 2, 3, 256, 257, 258, 259, 512, 513, 514, 515, 768,
#                769, 770, 771]

class Result(BaseModel):
    cdays: int
    remainday: int
    ok: int
    title: str
    itype: int
    ntype: int
    message: dict
    coin: int


class ItHomeTask(Task):
    """
    https://github.com/daimiaopeng/IthomeQianDao
    """
    name: ClassVar[str] = "IT之家"

    username: str
    password: str

    @staticmethod
    def encrypt(data: str, key: str) -> str:
        """
        :param data: 待加密数据
        :param key: 密钥
        :return: 加密后的16进制字符串
        """
        data = data.encode()
        data = data + b"\x00" * (8 - len(data) % 8)
        cipher = Cipher(
            algorithms.TripleDES(key.encode()),
            modes.ECB(),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        en = encryptor.update(data) + encryptor.finalize()
        return binascii.b2a_hex(en).decode()

    @staticmethod
    def en_timestamp(
        dt: datetime.datetime,
        length: int,
        offset: int = 0
    ) -> str:
        day = dt.day  # 当月第几日
        timestamp = int(dt.timestamp() * 1000)
        ts = round(timestamp / 50000) * day * 3

        out = [
            STRING_LIST[int(ts % pow(10, i) / pow(10, i - 1)) * day]
            for i
            in range(length + offset, offset, -1)
        ]

        return ''.join(out)

    def get_sign_params(self):
        now = datetime.datetime.now()
        ts = int(now.timestamp() * 1000)

        key = 'k' + self.encrypt(
            self.en_timestamp(now, 3, offset=1),
            self.en_timestamp(now, 8),
        )
        val = self.encrypt(
            now.strftime("%Y-%m-%d %H:%M:%S"),
            self.en_timestamp(now, 8),
        )
        return ts, key, val

    def get_user_hash(self, cookie_str):
        pattern = r"user=hash=[a-zA-Z0-9]{160,160}"
        return re.search(pattern, cookie_str).group()[10:]

    def login(self) -> str:
        url = 'https://my.ruanmei.com/Default.aspx/LoginUser'
        data = {
            'mail': self.username,
            'psw': self.password,
            'rememberme': 'true'
        }
        header = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/json; charset=UTF-8',
            'Host': 'my.ruanmei.com',
            'Origin': 'http://my.ruanmei.com',
            'Referer': 'http://my.ruanmei.com/',
            'User-Agent': ithome,
            'X-Requested-With': 'XMLHttpRequest',
        }
        response = httpx.post(url=url, json=data, headers=header)
        return self.get_user_hash(response.headers['Set-Cookie'])

    def process(self):
        url = "https://my.ruanmei.com/api/usersign/sign"
        headers = {
            'user-agent': ithome,
            'content-type': 'application/x-www-form-urlencoded',
            'accept': '*/*',
            'x-requested-with': 'com.ruanmei.ithome',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': ('https://my.ruanmei.com/app/user/signin.html?'
                        'hidemenu=1&appver=2'),
        }

        ts, sign_key, sign_val = self.get_sign_params()
        params = {
            "userHash": self.login(),
            "type": 0,  # 其他的已经失效
            "endt": "",
            "timestamp": ts,
            sign_key: sign_val,
        }

        data = httpx.get(url=url, params=params, headers=headers).json()
        self.debug(data)
        if data["ok"] == 1:
            result = Result.model_validate(data)
            self.notify(f"{result.title}, {result.message['签到奖励']}")
        else:
            self.notify(data["msg"])
