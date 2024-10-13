import datetime
import html
import random
import re

from aiogram.dispatcher.filters import ChatTypeFilter, Regexp, IsReplyFilter
from aiogram.types import ChatType, Message, ChatMemberStatus
from asyncpg import Pool

from data.config import time_delta, time_delta_postgres
from loader import dp, prefixes, name_of_bot, interval_available, ranks, commands_id, commands_normal_dict, max_len_text
from utils.dop_func import get_mention, get_nickname, get_interval_from_str, get_user_id, check_if_has_permission, \
    get_profile


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), Regexp(r"(?is)^"+prefixes+r"?правила[\n]+(?P<rules>.+)"))
async def add_rules(message : Message, pool : Pool):
    await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool = pool, command_name="правила")

    match = re.search(r"(?is)"+prefixes+r"?правила[\n]+(?P<rules>.+)", message.text)
    rules = match.group("rules")
    async with pool.acquire() as con:
        await con.execute(f'''Update groups set rules = '{rules.replace("'","''")}' where chat_id = {message.chat.id}''')
    await message.answer("✅Правила чату оновлено")

@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), Regexp(r"(?is)^"+prefixes[:-1]+r"правила"))
async def del_rules(message : Message, pool : Pool):

    await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool=pool, command_name="правила")

    async with pool.acquire() as con:
        await con.execute(f'''Update groups set rules = null where chat_id = {message.chat.id}''')
    await message.answer("❎ Правила чату видалено")


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), Regexp(r"(?is)^"+prefixes+r"?вітання[\n]+(?P<hello>.+)"))
async def get_rules(message : Message, pool : Pool):
    await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool=pool,command_name="вітання")

    match = re.search(r"(?is)^"+prefixes+r"?приветствие[\n]+(?P<hello>.+)", message.text)
    hello_message = match.group("hello")

    async with pool.acquire() as con:
        await con.execute(f'''Update groups set hello_message = '{hello_message.replace("'","''")}' where chat_id = {message.chat.id}''')
    await message.answer("✅ Вітання нових користувачів у чаті оновлено")


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), Regexp(r"(?is)^"+r"-приветствие"))
async def del_rules(message : Message, pool : Pool):
    await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool=pool, command_name="вітання")
    async with pool.acquire() as con:
        await con.fetchval(f'''update groups set hello_message = null where chat_id = {message.chat.id}''')

    await message.answer("❎ Вітання нових користувачів у чаті видалено")


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), Regexp(r"(?is)^"+prefixes+r"вітання"))
async def del_rules(message : Message, pool : Pool):
    await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool=pool, command_name="вітання")

    async with pool.acquire() as con:
        hello_message = await con.fetchval(f'''select hello_message from groups where chat_id = {message.chat.id}''')
        if not hello_message:
            await message.answer("🗓 Вітання чату поки не встановлено")
            return

    await message.answer("🗓 Вітання чату:\n"+hello_message)


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"список\s+команд"))
async def top_active(message: Message, pool: Pool):
    await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool=pool, command_name="список команд")
    text = "Нижче наведені назви команд:\n\n"
    for ind, value in enumerate(commands_normal_dict.values()):
        text+=str(ind) + f". {value}\n"
    await message.answer(text)



@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), Regexp(r"(?is)^"+prefixes+r"позвати\s+всіх"))
async def add_rules(message : Message, pool : Pool):
    await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool = pool, command_name="позвати всіх")
    async with pool.acquire() as con:
        last_time_general_meeting = await con.fetchval(f'''select last_time_general_meeting from groups where chat_id = {message.chat.id}''')

        if datetime.datetime.now() + time_delta < last_time_general_meeting + datetime.timedelta(minutes=15):
            await message.answer(f'''
📝 Цю команду можна використовувати тільки раз в 15 хвилин
⏱ Обмеження буде знято {(last_time_general_meeting + datetime.timedelta(minutes=15)).strftime("%H:%M:%S")}''')
            return

        users = await con.fetch(f'''select user_id from users where chat_id = {message.chat.id}''')
        profile = await get_profile(message.chat.id, message.from_user.id, con)
        await con.execute(f'''update groups set last_time_general_meeting = '{datetime.datetime.now() + time_delta}'::timestamp where chat_id = {message.chat.id}''')
        text = f'''📢 Модератор {get_mention(profile['user_id'], get_nickname(profile))} обявив загальний збір! ({len(users)})'''

        for user in users:
            if len(text + f'<a href="tg://user?id={user["user_id"]}">⁬</a>')>=max_len_text:
                await message.answer(text)
                text = ""
                continue
            text+= f'<a href="tg://user?id={user["user_id"]}">⁬</a>'

        await message.answer(text)

