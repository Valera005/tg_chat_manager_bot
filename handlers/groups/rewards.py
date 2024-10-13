import re

from aiogram.dispatcher.filters import ChatTypeFilter, Regexp, IsReplyFilter
from aiogram.types import Message, ChatType
from asyncpg import Pool

from data.config import time_delta
from loader import prefixes, interval_available, dp, rewards_id
from utils.dop_func import get_user_id, check_if_has_permission, get_profile, get_mention, get_nickname


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"нагородити[. ,!;]+@(?P<link>[\w\d]+)([ \n]+(?P<description>.+)?)?"))
@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),IsReplyFilter(is_reply=True),Regexp(r"(?is)^" + prefixes + fr"нагородити([ \n]+(?P<description>.+)?)?"))
async def warn_someone(message: Message, pool: Pool, regexp):


    d = regexp.groupdict()
    d['power'] = '1'
    if message.reply_to_message:
        d['link'] = str(message.reply_to_message.from_user.id)


    if not d['description']:
        await message.answer(f'''📝 Не вказано опис нагороди''')
        return


    async with pool.acquire() as con:
        accused_user_id = await get_user_id(d['link'], con)
        if accused_user_id == message.from_user.id:
            await message.answer("Нельзя выдавать награду себе")
            return
        await con.execute(f'''insert into rewards(chat_id, user_id, datetime, description, moderator_user_id, power) values 
        ({message.chat.id}, {accused_user_id}, '{(message.date + time_delta).strftime("%Y-%m-%d %H:%M:%S")}'::timestamp,  
        '{d['description'].replace("'", "''") if d['description'] else None}', {message.from_user.id}, {d['power']})'''.replace("'None'", "null"))

        profile = await get_profile(message.chat.id, accused_user_id, con)
        await message.answer(f"✅ {get_mention(profile['user_id'], get_nickname(profile))} було нагороджено")


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), Regexp(r"(?is)^" + prefixes + fr"нагороди[. ,!;]+@(?P<link>[\w\d]+)"))
@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), IsReplyFilter(is_reply=True), Regexp(r"(?is)^" + prefixes + fr"нагороди"))
async def warn_someone(message: Message, pool: Pool, regexp):

    d = regexp.groupdict()
    if message.reply_to_message:
        d = {'link' : str(message.reply_to_message.from_user.id)}

    async with pool.acquire() as con:
        accused_user_id = await get_user_id(d['link'], con)
        rewards = await con.fetch(f'''select rewards.*, profiles.full_name, profiles.nickname, 
                    (select full_name moderator_full_name from profiles where user_id = rewards.moderator_user_id) 
                    from rewards inner join profiles on rewards.user_id = profiles.user_id 
                    where rewards.chat_id = {message.chat.id} and rewards.user_id = {accused_user_id} order by id limit 10''')

        if not rewards:
            await message.answer(f'''🏆 Нагород поки немає''')
            return


        text = f'''🏆 Нагороди {get_mention(rewards[0]['user_id'], get_nickname(rewards[0]))}:'''

        for ind, reward in enumerate(rewards, start=1):
            text += f'''
{ind}. {reward['description']}
⏱ Видано {reward['datetime'].strftime("%d.%m.%Y %H:%M")}
'''
        await message.answer(text)


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), Regexp(r"(?is)^" + prefixes + fr"зняти\s+всі\s+нагороди\s+@(?P<link>[\w\d]+)"))
@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), IsReplyFilter(is_reply=True), Regexp(r"(?is)^" + prefixes + fr"зняти\s+всі\s+нагороди"))
async def warn_someone(message: Message, pool: Pool, regexp):

    d = regexp.groupdict()
    if message.reply_to_message:
        d = {'link': str(message.reply_to_message.from_user.id)}

    async with pool.acquire() as con:
        accused_user_id = await get_user_id(d['link'], con)
        await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool=pool,
                                      command_name="зняття нагород")
        await con.execute(f'''delete from rewards where chat_id = {message.chat.id} and user_id = {accused_user_id}''')

    await message.answer(f'✅ Всі нагороди видалені')


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), Regexp(r"(?is)^" + prefixes + fr"зняти\s+нагороду\s+(?P<num>\d+)\s+@(?P<link>[\w\d]+)"))
@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), IsReplyFilter(is_reply=True), Regexp(r"(?is)^" + prefixes + fr"зняти\s+нагороду\s+(?P<num>\d+)"))
async def warn_someone(message: Message, pool: Pool, regexp):

    d = regexp.groupdict()
    if message.reply_to_message:
        d['link'] = str(message.reply_to_message.from_user.id)

    async with pool.acquire() as con:
        accused_user_id = await get_user_id(d['link'], con)
        await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool=pool,
                                      command_name="зняття нагород")
        await con.execute(f'''delete from rewards where chat_id = {message.chat.id} and user_id = {accused_user_id} and id = (select id from rewards where 
        chat_id = {message.chat.id} and user_id = {accused_user_id} order by id offset ({d['num']} - 1) limit 1)''')
        profile = await get_profile(message.chat.id, accused_user_id, con)

    await message.answer(f'❎ Нагорода {d["num"]} була знята з {get_mention(profile["user_id"], get_nickname(profile))}')


