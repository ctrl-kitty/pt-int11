import asyncio
import time
import logging
import aiogram
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
import os

import requests


class MergeRequest:
    request_url: str
    title: str
    auth_username: str

    def __init__(self, request_url: str, title: str, author_username: str):
        self.request_url = request_url
        self.title = title
        self.author_username = author_username

    def get_telegram_str(self):
        return f'[Merge Request by @{self.author_username}] <a href="{self.request_url}">{self.title}</a>'

    def __repr__(self):
        return f"Merge Request: {self.title}"


class GitlabAPI:
    url: str
    token: str
    project_id: str
    _headers: dict[str, str]
    _logger: logging.Logger

    def __init__(self, url: str, token: str, project_id: str):
        self.url = url
        self.token = token
        self.project_id = project_id
        self._headers = {"Private-Token": token}
        self._logger = logging.getLogger("GitlabAPI")

    def get(self, path: str, *args, **kwargs):
        return requests.get(self.url + path, headers=self._headers, *args, **kwargs)

    def post(self, path: str, data: dict, *args, **kwargs):
        return requests.post(self.url + path, data=data, headers=self._headers, *args, **kwargs)

    def put(self, path: str, data: dict, *args, **kwargs):
        return requests.put(self.url + path, data=data, headers=self._headers, *args, **kwargs)

    def get_new_merge_requests(self):
        data = self.get(f"/merge_requests?state=opened").json()
        return [
            MergeRequest(
                request_url=merge_request.get("web_url"),
                title=merge_request.get("title"),
                author_username=merge_request.get("author").get("username"),
            ) for merge_request in data
        ]


async def bot_send_notifications(bot: aiogram.Bot, chat_ids: tuple[int], text: str):
    for chat_id in chat_ids:
        await bot.send_message(chat_id, text)


async def main():
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
    GITLAB_URL = os.getenv("GITLAB_URL")
    GITLAB_PROJECT_ID = os.getenv("GITLAB_PROJECT_ID")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    NOTIFICATION_TIMEOUT = int(os.getenv("NOTIFICATION_TIMEOUT"))
    TELEGRAM_CHAT_IDS = tuple(map(int, os.getenv("TELEGRAM_CHAT_IDS").split()))
    bot = aiogram.Bot(TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    gitlab_api = GitlabAPI(token=GITLAB_TOKEN, url=GITLAB_URL, project_id=GITLAB_PROJECT_ID)
    while 1:
        active_requests = gitlab_api.get_new_merge_requests()
        if active_requests:
            notification_text = "Active merge requests:\n"
            notification_text += "\n".join(mr.get_telegram_str() for mr in active_requests)
            await bot_send_notifications(bot=bot, text=notification_text, chat_ids=TELEGRAM_CHAT_IDS)
        time.sleep(NOTIFICATION_TIMEOUT)


if __name__ == '__main__':
    asyncio.run(main())
