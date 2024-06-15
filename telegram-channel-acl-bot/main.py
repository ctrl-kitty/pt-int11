import asyncio
import os
from pyrogram import Client
from dotenv import load_dotenv


class TgUser:
    id: int
    tag: str | None
    phone_number: str | None
    first_name: str
    last_name: str | None

    def __init__(self, id: int, first_name: str, tag: str = None, phone_number: str = None, last_name: str = None):
        self.id = id
        self.tag = tag
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name

    def __str__(self):
        res = f'<a href="tg://user?id={self.id}">Пользователь</a> не является сотрудником, но зашёл в канал\n'
        res += f'Ник: {self.first_name} {self.last_name}\n'
        if self.tag:
            res += f'Тэг: @{self.tag}\n'
        if self.phone_number:
            res += f'Номер телефона: {self.phone_number}\n'
        return res


def read_employees_list() -> set[int]:
    res = set()
    with open('employees', 'r') as file:
        for line in file.readlines():
            res.add(int(line))
    return res


async def notify_admins(bot: Client, admin_ids: tuple[int, ...], violated_users: list[TgUser]) -> None:
    text = "\n".join(str(user) for user in violated_users)
    for admin_id in admin_ids:
        await bot.send_message(chat_id=admin_id, text=text)


async def get_violated_users(acl: set[int], users: list[TgUser]) -> list[TgUser]:
    res = []
    for user in users:
        if user.id not in acl:
            res.append(user)
    return res


async def check_acl(bot: Client, bot_id: int, chat_id: int, admin_ids: tuple[int, ...]) -> None:
    allowed_list = read_employees_list()
    allowed_list.add(bot_id)
    channel_members = []
    async for m in bot.get_chat_members(chat_id=chat_id):
        channel_members.append(TgUser(
            id=m.user.id,
            tag=m.user.username,
            phone_number=m.user.phone_number,
            first_name=m.user.first_name,
            last_name=m.user.last_name
        ))
    violated_users = await get_violated_users(allowed_list, channel_members)
    await notify_admins(bot=bot, admin_ids=admin_ids, violated_users=violated_users)


async def main():
    load_dotenv()
    bot = Client(name="bot", bot_token=os.getenv("TELEGRAM_TOKEN"), api_id=os.getenv("API_ID"),
                 api_hash=os.getenv("API_HASH"))
    await bot.start()
    bot_id = (await bot.get_me()).id
    admin_ids = tuple(map(int, os.getenv("TELEGRAM_ADMIN_IDS").split()))

    check_interval = int(os.getenv("CHECK_INTERVAL"))

    while 1:
        await check_acl(bot=bot, bot_id=bot_id, chat_id=int(os.getenv("TELEGRAM_CHANNEL_ID")), admin_ids=admin_ids)
        await asyncio.sleep(check_interval)


if __name__ == '__main__':
    asyncio.run(main())
