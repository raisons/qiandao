#!/usr/bin/env python
import httpx
import copy
import time
from typing import ClassVar, Optional
from task.base import Task
from task.useragents import safari

HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Host": None,
    "Discourse-Logged-In": "true",
    "Discourse-Present": "true",
    "Discourse-Track-View": "true",
    "User-Agent": safari,
    "Referer": None,
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "X-Requested-With": "XMLHttpRequest",
}


class DiscourseTask(Task):
    domain: ClassVar[str] = None

    cookies: str
    csrf_token: str
    username: Optional[str] = None

    def get_http_client(self):
        headers = copy.deepcopy(HEADERS)
        headers["Referer"] = f"https://{self.domain}/"
        headers["Host"] = self.domain
        headers["X-CSRF-Token"] = self.csrf_token

        return httpx.Client(
            base_url=f"https://{self.domain}",
            cookies=self.split_cookie(self.cookies),
            proxies=self.get_http_proxies(),
            headers=headers
        )

    def _fetch_topics(self, url, **params):
        response = self.client.get(url, params=params)
        return response.json()["topic_list"]["topics"]

    def get_latest_topics(self, order="created"):
        return self._fetch_topics("/latest.json", order=order)

    def get_top_topics(self, period="daily"):
        return self._fetch_topics("/top.json", period=period)

    def get_new_topics(self):
        return self._fetch_topics("/new.json")

    def get_unread_topics(self):
        return self._fetch_topics("/unread.json")

    def timings(self, data):
        return self.client.post("/topics/timings", data=data)

    def get_topic_detail(self, topic_id: int):
        response = self.client.get(
            f"/t/{topic_id}.json?track_visit=true"
        )
        return response.raise_for_status().json()

    def get_summary(self, username):
        response = self.client.get(f"/u/{username}/summary.json")
        user = response.json()["user_summary"]
        print("用户名:", username)
        print("访问天数:", user["days_visited"])
        print("帖子阅读时间:", f"{user['time_read'] // 3600}小时")
        print("浏览的话题数:", user["topics_entered"])
        print("帖子阅读数量:", user["posts_read_count"])
        print("访问天数:", user["days_visited"])
        print("送出点赞:", user["likes_given"])
        print("收到点赞:", user["likes_received"])
        print("创建话题:", user["topic_count"])
        print("创建帖子:", user["post_count"])

    def topics_timings(
        self,
        topic_id: int,
        highest_post_num: int,
        last_read_post_num: int,
        read_time: int = 10000
    ):
        if last_read_post_num is None:
            last_read_post_num = 0
        read_count = highest_post_num - last_read_post_num
        data = {
            "topic_id": topic_id,
            "topic_time": 0
        }
        for i in range(last_read_post_num, highest_post_num + 1):
            data["topic_time"] += read_time
            data[f'timings[{i}]'] = data["topic_time"]

        response = self.timings(data=data)
        if response.status_code == 200:
            return read_count
        return 0

    def like_post(self, post_id):
        response = self.client.put(
            f"/discourse-reactions/posts/{post_id}"
            f"/custom-reactions/heart/toggle.json"
        )

        if response.status_code == 200:
            self.log(f"Successfully liked post: {post_id}")
            return 1

        elif response.status_code == 429:
            # self.states['liked_topics'] = 75
            # now = datetime.datetime.now()
            resp = response.json()
            wait_seconds = resp["extras"]["wait_seconds"]
            # target_time = now + datetime.timedelta(seconds=wait_seconds)
            # self.states['liked_wait_until'] = target_time.isoformat()
            self.log(f'当前点赞到上限，再等待{resp["extras"]["time_left"]}')
            return -429

        else:
            self.log(f"Failed to like post: {post_id}")
            self.log(response.status_code, response.text)

        return 0

    def auto_read_posts(self, topics):
        total_read_posts = 0
        for topic in topics:
            read_count = self.topics_timings(
                topic["id"],
                topic["highest_post_number"],
                topic.get("last_read_post_number", None)
            )
            total_read_posts += read_count
            self.log(f"读取topic {topic['id']}, {read_count}条评论")
            time.sleep(1)

        self.log(f'成功标记 {total_read_posts} posts 为读取')

    def auto_like(self):
        total_liked_topics = 0
        topics = self.get_new_topics()
        for topic in topics:
            if topic["unseen"]:
                topic_info = self.get_topic_detail(topic["id"])
                post_stream = topic_info["post_stream"]
                first_post = post_stream["posts"][0]

                like_count = self.like_post(first_post["id"])
                if like_count == -429:
                    break
                total_liked_topics += like_count

                time.sleep(1)
        self.log(f"送出点赞：{total_liked_topics}个")

    def process(self):
        # await self.auto_read_posts(await self.topic.unread())
        # await self.auto_read_posts(await self.topic.new())
        # await self.auto_read_posts(await self.topic.top())
        # await self.auto_read_posts(await self.topic.latest())
        self.auto_like()
        if self.username:
            self.get_summary(self.username)


class LinuxDoTask(DiscourseTask):
    domain: ClassVar[str] = "linux.do"
