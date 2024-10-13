import datetime
import re

import asyncpg
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message, ChatType, MessageEntityType
from aiogram.utils.exceptions import ChatNotFound, BadRequest
from asyncpg import UniqueViolationError, Pool

from data.config import time_delta
from loader import bot


async def try_delete(message:Message, success_text: str):
    try:
        await message.delete()
    except BadRequest:
        await message.answer("Не можу видалити повідомлення, недостатньо прав")

    await message.answer(success_text)


class CheckBeforeProcessing(BaseMiddleware):

    def __init__(self, pool):
        super().__init__()
        self.pool = pool
        self.tg_link_regexp = re.compile("(?i)(https://)?t\.me/(?P<username>.+)")

    async def on_pre_process_message(self, message : Message, data : dict):
        if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            data['nickname'] = message.from_user.full_name
            return


        async with self.pool.acquire() as con:
            group_info : asyncpg.Record = await con.fetchrow(f'''select can_send_messages, is_urls, is_talks, is_groups, is_channels from groups where chat_id = {message.chat.id}''')

            if not group_info:
                chat = message.chat
                admins = await chat.get_administrators()

                owner_user_id = None
                for admin in admins:
                    try:
                        if admin.is_chat_creator():
                            owner_user_id = admin.user.id
                            await con.execute(
                                f'''insert into users(chat_id,user_id, rank, datetime) values({chat.id}, {admin.user.id} , 4,
                                '{(datetime.datetime.now() + time_delta).strftime("%Y-%m-%d %H:%M:%S")}'::timestamp)''')
                        else:
                            await con.execute(
                                f'''insert into users(chat_id,user_id, rank, datetime) values({chat.id}, {admin.user.id} , 1,
                                '{(datetime.datetime.now() + time_delta).strftime("%Y-%m-%d %H:%M:%S")}'::timestamp)''')
                    except UniqueViolationError:
                        pass

                try:
                    group_info = await con.fetchrow(f'''Insert into groups(chat_id, title, username, type, chat_member_type, date_of_addition, date_of_edit, owner_user_id) values 
                                ({chat.id}, '{chat.title.replace("'", "''") if chat.title else None}', '{chat.username}', '{chat.type}', 'member', 
                                '{message.date.strftime("%Y-%m-%d %H:%M:%S")}'::timestamp, '{message.date.strftime("%Y-%m-%d %H:%M:%S")}'::timestamp, 
                                {owner_user_id if owner_user_id else "'None'"}) returning can_send_messages'''.replace("'None'", "null"))
                except UniqueViolationError:
                    await con.execute(f'''Update groups set can_send_messages = true, chat_member_type = 'member', date_of_edit = '{message.date.strftime("%Y-%m-%d %H:%M:%S")}'::timestamp where chat_id = {chat.id}''')

                sql = f'''insert into commands(chat_id, command_id, rank) values'''
                for command_id in range(1, 101):
                    sql += f" ({chat.id}, {command_id}, 1),"

                sql += f" ({chat.id}, 1000, 4),"
                sql = sql[:-1]
                sql += " ON CONFLICT(chat_id, command_id) DO NOTHING"
                try:
                    await con.execute(sql)
                except UniqueViolationError:
                    pass

            can_send_messages = group_info['can_send_messages'] if group_info else True

            if message.text:
                for entity in message.entities:

                    entity_text = entity.get_text(message.text)

                    if not group_info['is_urls'] and entity.type == MessageEntityType.URL and not re.search(self.tg_link_regexp, entity_text):

                        await try_delete(message,"Посилання на сторонні сайти заборонені, щоб прибрати це повідомлення введіть +сайти")
                        break

                    elif (not group_info['is_groups'] or not group_info['is_talks'] or not group_info['is_channels']) and  entity.type == MessageEntityType.MENTION:
                        try:
                            chat = await bot.get_chat(chat_id=entity_text)

                            if (not group_info['is_groups'] or not group_info['is_talks']) and  chat.type in [ChatType.GROUP, ChatType.SUPERGROUP] and chat.id != message.chat.id:
                                await try_delete(message,
                                    "Посилання на сторонні групи заборонені, щоб прибрати це повідомлення введіть +групи")
                                break

                            elif not group_info['is_channels'] and  chat.type in [ChatType.CHANNEL] and chat.id != message.chat.id:
                                await try_delete(message, "Посилання на сторонні канали заборонені, щоб прибрати це повідомлення введіть +канали")
                                break

                        except ChatNotFound:
                            pass

                    elif (not group_info['is_groups'] or not group_info['is_talks'] or not group_info['is_channels']) and entity.type == MessageEntityType.URL and re.search(self.tg_link_regexp, entity_text):
                        match = re.search(self.tg_link_regexp, entity_text)
                        username = match.group("username")

                        if username[0]=="+":
                            await try_delete(message,
                                             "Посилання на сторонні групи заборонені, щоб прибрати це повідомлення введіть +групи")
                            break

                        else:
                            username = "@" + username
                            try:
                                chat = await bot.get_chat(chat_id=username)
                                if (not group_info['is_groups'] or not group_info['is_talks']) and chat.type in [ChatType.GROUP, ChatType.SUPERGROUP] and chat.id != message.chat.id:

                                    await try_delete(message,"Посилання на сторонні групи заборонені, щоб прибрати це повідомлення введіть +групи")
                                    break

                                elif not group_info['is_channels'] and chat.type in [ChatType.CHANNEL] and chat.id != message.chat.id:
                                    await try_delete(message,"Посилання на сторонні канали заборонені, щоб прибрати це повідомлення введіть +канали")
                                    break

                            except ChatNotFound:
                                pass





            if not can_send_messages:
                raise CancelHandler
