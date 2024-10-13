import datetime
import re

from aiogram.dispatcher.filters import IsReplyFilter, Regexp, ChatTypeFilter
from aiogram.types import Message, ChatType
from aiogram.utils.exceptions import TelegramAPIError, BadRequest
from asyncpg import Pool, UniqueViolationError

from data.config import time_delta, time_delta_postgres
from loader import prefixes, dp, interval_available
from utils.dop_func import get_mention, get_user_id, get_nickname, get_profile, get_interval_from_str, \
    check_if_has_permission

@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), IsReplyFilter(is_reply=True),Regexp(r"(?is)^" + prefixes + fr"варн[. ,!;]+(?P<interval>\d+\s+{interval_available})([ \n]+(?P<description>.+)?)?"))
@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), Regexp(r"(?is)^" + prefixes + fr"варн[. ,!;]+(?P<interval>\d+\s+{interval_available})\s+@(?P<link>[\w\d]+)([ \n]+(?P<description>.+)?)?"))
@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), Regexp(r"(?is)^" + prefixes + fr"варн[. ,!;]+@(?P<link>[\w\d]+)([ \n]+(?P<description>.+)?)?"))
async def warn_someone(message: Message, pool: Pool, regexp):

    d = regexp.groupdict()

    if message.reply_to_message:
        d['link'] = str(message.reply_to_message.from_user.id)
    if not d['interval']:
        d['interval'] = "1 тиждень"
    if d['description']:
        description = d['description']
    else:
        description = None

    async with pool.acquire() as con:
        accused_user_id = await get_user_id(d['link'], con)

        await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id,
                                      accused_user_id=accused_user_id, pool=pool, command_name="варн")

        await con.execute(f'''Insert into warns(chat_id, user_id, datetime, datetime_of_expiration, description, moderator_user_id) values 
        ({message.chat.id}, {accused_user_id}, '{(message.date+time_delta).strftime("%Y-%m-%d %H:%M:%S")}'::timestamp, 
        '{(message.date+time_delta).strftime("%Y-%m-%d %H:%M:%S")}'::timestamp + '{get_interval_from_str(d['interval'])}'::interval, '{description.replace("'","''") if description else None}', {message.from_user.id})'''.replace("'None'", "null"))

        num_of_warns = await con.fetchval(
            f'''select count(1) from warns where chat_id = {message.chat.id} and user_id = {accused_user_id} and datetime_of_expiration>(now() + {time_delta_postgres})''')
        max_warns = await con.fetchval(f'''select max_warns from groups where chat_id = {message.chat.id}''')
        profile = await get_profile(message.chat.id, accused_user_id, con)

        admins = await message.chat.get_administrators()
        owner = None
        for admin in admins:
            if admin.is_chat_owner:
                owner = admin
                break

        if num_of_warns>=max_warns:
            await con.execute(f'''delete from warns where chat_id = {message.chat.id} and user_id = {accused_user_id}''')
            await dp.bot.ban_chat_member(chat_id=message.chat.id, user_id=accused_user_id)
            await message.answer(f'''
🔴 Досягнуто ліміту попереджень
{get_mention(profile['user_id'], get_nickname(profile))}, бан назавжди
Якщо хочеш повернутись, напиши <a href='tg://openmessage?user_id={owner.user.id}'>власнику чата</a>''')
            return

        await message.answer(f'''
❗️ {get_mention(profile['user_id'], get_nickname(profile))} отримує попередження ({num_of_warns}/{max_warns})
Будет снято через {d['interval']}
Модератор: {message.from_user.get_mention()}
{('💬 Причина: ' + description) if description else ""}''')


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), Regexp(r"(?is)^" + prefixes + fr"варн лист"))
async def warn_list(message: Message, pool: Pool):
    text = "🗓 Список останніх попереджень користувачів чату:\n"
    await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool=pool,command_name="варн лист")

    async with pool.acquire() as con:
        warns = await con.fetch(f'''select warns.*, profiles.full_name, profiles.nickname, 
        (select full_name moderator_full_name from profiles where user_id = warns.moderator_user_id) 
        from warns inner join profiles on warns.user_id = profiles.user_id where chat_id = {message.chat.id} order by datetime_of_expiration desc limit 10''')

        if not warns:
            await message.answer(text + "💬 Пока список пуст")
            return

        n = '\n'
        for ind, warn in enumerate(warns, start=1):
            text+=f'''
<b>{ind}. {get_mention(warn['user_id'], warn['full_name'])}</b> [{warn['id']}]
⏱ До {warn['datetime_of_expiration'].strftime("%d.%m.%Y %H:%M")}{(n+'💬 Причина: ' + warn['description']) if warn['description'] else ""}
Модератор: {get_mention(warn['moderator_user_id'], warn['moderator_full_name'])}
'''
        await message.answer(text)


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),IsReplyFilter(is_reply=True), Regexp(r"(?is)^" + prefixes + fr"варни"))
@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), Regexp(r"(?is)^" + prefixes + fr"варни[. ,!;]+@(?P<link>[\w\d]+)"))
async def warn_list(message: Message, pool: Pool, regexp):

    d = regexp.groupdict()
    if message.reply_to_message:
        d = {"link": message.reply_to_message.from_user.id}

    async with pool.acquire() as con:
        accused_user_id = await get_user_id(d['link'], con)
        await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool=pool,command_name="варни")

        warns = await con.fetch(f'''select warns.*, profiles.full_name, profiles.nickname, 
        (select full_name moderator_full_name from profiles where user_id = warns.moderator_user_id) 
        from warns inner join profiles on warns.user_id = profiles.user_id where warns.chat_id = {message.chat.id} and warns.user_id = {accused_user_id} order by datetime_of_expiration desc limit 10''')

        if not warns:
            await message.answer("❕ У данного користувача немає попереджень")
            return

        text = f"❕ Попередження {get_mention(warns[0]['user_id'], warns[0]['full_name'])}:\n"

        n = '\n'
        for ind, warn in enumerate(warns, start=1):
            text+=f'''
<b>{ind}. От {get_mention(warn['moderator_user_id'], warn['moderator_full_name'])}</b> [{warn['id']}]
⏱ До {warn['datetime_of_expiration'].strftime("%d.%m.%Y %H:%M")}{(n+'💬 Причина: ' + warn['description']) if warn['description'] else ""}
'''
        await message.answer(text)


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),IsReplyFilter(is_reply=True), Regexp(r"(?is)^" + prefixes + fr"варн(и)?\s+ліміт(?P<max_warns>\d+)"))
async def warn_list(message: Message, pool: Pool, regexp):

    d = regexp.groupdict()
    await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool=pool, command_name="варн ліміт")

    async with pool.acquire() as con:
        await con.execute(f'''update groups set max_warns = {d['max_warns']} where chat_id = {message.chat.id}''')

    await message.answer(f"✅ Ліміт попереджень змінено на {d['max_warns']}")


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"бан[. ,!;]+(?P<interval>\d+\s+{interval_available})\s+@(?P<link>[\w\d]+)([ \n]+(?P<description>.+)?)?"))
@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"бан[. ,!;]+@(?P<link>[\w\d]+)([ \n]+(?P<description>.+)?)?"))
@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),IsReplyFilter(is_reply=True), Regexp(r"(?is)^" + prefixes + fr"бан[. ,!;]+(?P<interval>\d+\s+{interval_available})([ \n]+(?P<description>.+)?)?"))
@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),IsReplyFilter(is_reply=True), Regexp(r"(?is)^" + prefixes + fr"бан([ \n]+(?P<description>.+)?)?"))
async def ban_someone(message: Message, pool: Pool, regexp):
 async with pool.acquire() as con:


    d = regexp.groupdict()
    d['interval'] = get_interval_from_str(d['interval'])

    if not d['interval']:
        d['interval'] = await con.fetchval(f'''select ban_interval from groups where chat_id={message.chat.id}''')

    if not d['link'] and message.reply_to_message:
        d['link'] = str(message.reply_to_message.from_user.id)

    if not d['description']:
        d['description'] = ""

    accused_user_id = await get_user_id(d['link'], con)
    is_exist = await con.fetchval(f'''select exists(select 1 from users where chat_id = {message.chat.id} and user_id = {accused_user_id})''')

    if not is_exist:
        await message.answer(f'''Користувач на даний момент не в бесіді''')
        return

    await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, accused_user_id= accused_user_id, pool=pool, command_name="бан")

    datetime_of_expiration : datetime.datetime= await con.fetchval(f'''select '{(message.date+time_delta).strftime("%Y-%m-%d %H:%M:%S")}'::timestamp + '{d['interval']}'::interval;''')

    await dp.bot.ban_chat_member(chat_id=message.chat.id, user_id=accused_user_id, until_date=datetime_of_expiration)

    await con.execute(f'''insert into bans(chat_id, user_id, datetime, datetime_of_expiration, description, moderator_user_id) values 
    ({message.chat.id}, {accused_user_id}, '{(message.date+time_delta).strftime("%Y-%m-%d %H:%M:%S")}'::timestamp, 
    '{(message.date+time_delta).strftime("%Y-%m-%d %H:%M:%S")}'::timestamp + '{d['interval']}'::interval, 
    '{d['description'].replace("'","''") if d['description'] else None}', {message.from_user.id})'''.replace("'None'", "null"))


    profile = await get_profile(message.chat.id, accused_user_id, con)

    n = '\n'
    await message.answer(f'''
🔴 {get_mention(profile['user_id'], get_nickname(profile))}
⏱ Бан до {datetime_of_expiration.strftime("%d.%m.%Y %H:%M")}{(n + '💬 Причина: ' + d['description']) if d['description'] else ""}
👤 Модератор: {message.from_user.get_mention()}''')


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"розбан[. ,!;]+@(?P<link>[\w\d]+)"))
@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),IsReplyFilter(is_reply=True), Regexp(r"(?is)^" + prefixes + fr"розбан"))
async def unban_someone(message: Message, pool: Pool, regexp):

    d = regexp.groupdict()
    if message.reply_to_message:
        d = {"link" : message.reply_to_message.from_user.id}


    await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool=pool, command_name="розбан")
    async with pool.acquire() as con:
        accused_user_id = await get_user_id(d['link'], con)

        await dp.bot.unban_chat_member(chat_id=message.chat.id, user_id=accused_user_id, only_if_banned=True)
        await con.execute(f'''delete from bans where user_id = {accused_user_id} and chat_id = {message.chat.id}''')
        profile = await get_profile(message.chat.id, accused_user_id, con)
        await message.answer(text=f'''✅ Користувач {get_mention(profile['user_id'], get_nickname(profile))} розбанений. Тепер його можна додати у чат''')



@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"бан лист"))
async def ban_list(message: Message, pool: Pool):
    text = "<b>🗓 Список останніх забанених користувачів бесіди:</b>\n"
    await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool=pool,command_name="бан лист")

    async with pool.acquire() as con:
        bans = await con.fetch(f'''select bans.*, profiles.full_name, profiles.nickname, 
            (select full_name moderator_full_name from profiles where user_id = bans.moderator_user_id) 
            from bans inner join profiles on bans.user_id = profiles.user_id where chat_id = {message.chat.id} order by datetime_of_expiration desc limit 10''')

        if not bans:
            await message.answer(text + "\n💬 Поки список пустий")
            return

        n = '\n'
        for ind, ban in enumerate(bans, start=1):
            text += f'''
<b>{ind}. {get_mention(ban['user_id'], ban['full_name'])}</b> [{ban['id']}]
⏱ До {ban['datetime_of_expiration'].strftime("%d.%m.%Y %H:%M")}{(n + '💬 Причина: ' + ban['description']) if ban['description'] else ""}
Забанив: {get_mention(ban['moderator_user_id'], ban['moderator_full_name'])}
'''
        await message.answer(text)


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"кік\s+актив\s+(?P<interval>\d+\s+{interval_available})"))
async def unban_someone(message: Message, pool: Pool, regexp):

    d = regexp.groupdict()
    interval = get_interval_from_str(d['interval'])

    await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool=pool, command_name="кік актив")

    async with pool.acquire() as con:
        interval_python : datetime.timedelta = await con.fetchval(f'''select '{interval}'::interval''')
        if interval_python>datetime.timedelta(hours=12):
            await message.answer(f'''Інтервал має бути менше 12 годин''')
            return
        users = await con.fetch(f'''select user_id from messages where datetime > now()+{time_delta_postgres}-'{interval}'::interval''')

    ban_interval = datetime.timedelta(minutes=1)
    suc_num = 0
    unsuc_num = 0
    for user in users:
        try:
            await dp.bot.ban_chat_member(chat_id=message.chat.id, user_id=user['user_id'], until_date=ban_interval)
            suc_num+=1
        except BadRequest:
            unsuc_num+=1

    await message.answer(f'''Учасники, які проявили активність протягом {d['interval']} були успішно вигнані
Успішно вигнано: {suc_num}
Не вдалось вигнати: {unsuc_num}''')



@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"кік\s+новачків\s+(?P<interval>\d+\s+{interval_available})"))
async def unban_someone(message: Message, pool: Pool, regexp):

    d = regexp.groupdict()
    interval = get_interval_from_str(d['interval'])

    await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool=pool, command_name="кік новачків")

    async with pool.acquire() as con:
        users = await con.fetch(f'''select user_id from users where datetime > now()+{time_delta_postgres}-'{interval}'::interval  ''')

    ban_interval = datetime.timedelta(minutes=1)
    suc_num = 0
    unsuc_num = 0
    for user in users:
        try:
            await dp.bot.ban_chat_member(chat_id=message.chat.id, user_id=user['user_id'], until_date=ban_interval)
            suc_num+=1
        except BadRequest:
            unsuc_num+=1

    await message.answer(f'''Учасники, які проявили активність протягом {d['interval']} були успішно вигнані
Успішно вигнано: {suc_num}
Не вдалось вигнати: {unsuc_num}''')



@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"кік\s+від\s+@(?P<link>[\w\d]+)"))
async def unban_someone(message: Message, pool: Pool, regexp):

    d = regexp.groupdict()

    async with pool.acquire() as con:
        accused_user_id = await get_user_id(d['link'], con)
        await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id,
                                      accused_user_id= accused_user_id, pool=pool, command_name="кік від")
        users = await con.fetch(f'''select user_id from users where invited_by = {accused_user_id}''')

    ban_interval = datetime.timedelta(minutes=1)
    suc_num = 0
    unsuc_num = 0
    for user in users:
        try:
            await dp.bot.ban_chat_member(chat_id=message.chat.id, user_id=user['user_id'], until_date=ban_interval)
            suc_num+=1
        except BadRequest:
            unsuc_num+=1

    await message.answer(f'''Учасники, які були додані юзером {d['link']} були успішно вигнані
Успішно вигнано: {suc_num}
Не вдалось вигнати: {unsuc_num}''')



@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"кік\s+@(?P<link>[\w\d]+)"))
@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),IsReplyFilter(is_reply=True),Regexp(r"(?is)^" + prefixes + fr"кік"))
async def unban_someone(message: Message, pool: Pool, regexp):

    d = regexp.groupdict()

    if message.reply_to_message:
        d = {"link": message.reply_to_message.from_user.id}


    async with pool.acquire() as con:
        accused_user_id = await get_user_id(d['link'], con)
        await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id,
                                      accused_user_id= accused_user_id, pool=pool, command_name="кік")

        profile = await get_profile(message.chat.id, accused_user_id,con)

    ban_interval = datetime.timedelta(minutes=1)
    try:
        await dp.bot.ban_chat_member(chat_id=message.chat.id, user_id=accused_user_id, until_date=ban_interval)
    except BadRequest as exc:
        await message.answer(f'''Не вдалось кікнути учасника, причина: {exc}''')

    await message.answer(f'''
🔴 {get_mention(profile['user_id'], get_nickname(profile))} був кікнутий
👤 Модератор: {message.from_user.get_mention()}
''')