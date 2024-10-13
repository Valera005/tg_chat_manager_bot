from aiogram.dispatcher.filters import ChatTypeFilter, Regexp
from aiogram.types import Message, ChatType
from asyncpg import Pool

from loader import prefixes, dp
from utils.dop_func import get_mention, get_nickname


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"топ[. ,!;]+активних[. ,!;]+тиждень"))
async def top_active(message: Message, pool: Pool):
    async with pool.acquire() as con:
        profiles = await con.fetch(f'''select (select count(1) from messages where user_id = users.user_id and chat_id = {message.chat.id}
        and current_date - datetime::date <= 7) as number_of_messages, profiles.* from users 
inner join profiles on users.user_id = profiles.user_id where users.chat_id = {message.chat.id} order by number_of_messages desc limit 10''')

    text = f'''Топ активних за тиждень:\n'''
    for profile in profiles:
        text +=f'''{get_nickname(profile)} - {profile['number_of_messages']} повідомлень\n'''

    await message.answer(text)



@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"топ[. ,!;]+активних([. ,!;]+сьогодні|[. ,!;]+день)?"))
async def top_active(message: Message, pool: Pool):
    async with pool.acquire() as con:
        profiles = await con.fetch(f'''select (select count(1) from messages where user_id = users.user_id and chat_id = {message.chat.id}
        and datetime::date = current_date) as number_of_messages, profiles.* from users 
inner join profiles on users.user_id = profiles.user_id where users.chat_id = {message.chat.id} order by number_of_messages desc limit 10''')

    text = f'''Топ активних за сьогодні:\n'''
    for ind, profile in enumerate(profiles, start=1):
        text +=f'''{ind}. {get_nickname(profile)} - {profile['number_of_messages']} повідомлень\n'''

    await message.answer(text)