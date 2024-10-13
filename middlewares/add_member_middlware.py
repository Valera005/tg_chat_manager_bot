import datetime
import random
import re


from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message, ContentType
from asyncpg import UniqueViolationError, CheckViolationError

from data.config import time_delta


class add_user(BaseMiddleware):

    def __init__(self, pool):
        super().__init__()
        self.pool = pool

    async def on_pre_process_message(self, message : Message, data:dict):
        async with self.pool.acquire() as con:
            if not message.from_user.is_bot:
                await con.execute(f'''insert into users(chat_id, user_id, datetime) values ({message.chat.id}, {message.from_user.id}, 
                            '{(datetime.datetime.now() + time_delta).strftime("%Y-%m-%d %H:%M:%S")}'::timestamp) ON CONFLICT(chat_id, user_id) DO NOTHING'''.replace("'None'", "null"))

                await con.execute(f'''update profiles set username = '{message.from_user.username}', first_name = '{message.from_user.first_name.replace("'","''")}',
                     full_name = '{message.from_user.full_name.replace("'","''")}' where user_id = {message.from_user.id}'''.replace("'None'", "null"))

                await con.execute(f'''insert into profiles(user_id, username, first_name, full_name) values
                                                    ({message.from_user.id}, '{message.from_user.username}', '{message.from_user.first_name.replace("'", "''")}',
                                                     '{message.from_user.full_name.replace("'", "''")}') ON CONFLICT(user_id) DO NOTHING'''.replace("'None'", "null"))


                if message.content_type == ContentType.TEXT:
                    await con.execute(f'''insert into messages(chat_id, user_id, message_thread_id, datetime, message_id) values
                                        ({message.chat.id}, {message.from_user.id}, {message.message_thread_id}, 
                                        '{(message.date + time_delta).strftime("%Y-%m-%d %H:%M:%S")}'::timestamp, {message.message_id})'''.
                                      replace("'None'", "null").replace("None", "null"))