import datetime
import re

from aiogram.dispatcher.filters import ChatTypeFilter, Regexp, IsReplyFilter
from aiogram.types import ChatType, Message, CallbackQuery
from asyncpg import Pool

from data.config import time_delta
from keyboards.inline.wedding_keyboard import get_wedding_keyboard, wedding_callback, get_divorce_keyboard
from loader import dp, prefixes
from utils.dop_func import get_user_id, get_profile, get_mention, get_nickname


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"брак\s+@(?P<link>[\w\d]+)"))
@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"одружитись\s+@(?P<link>[\w\d]+)"))
@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),IsReplyFilter(is_reply=True),Regexp(r"(?is)^" + prefixes + fr"одружитись"))
@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),IsReplyFilter(is_reply=True), Regexp(r"(?is)^" + prefixes + fr"брак"))
async def weddings_1(message: Message, pool: Pool, regexp):
    d = regexp.groupdict()

    if not d['link'] and message.reply_to_message:
        d = {"link":str(message.reply_to_message.from_user.id)}

    async with pool.acquire() as con:
        accused_user_id = await get_user_id(d['link'], con)
        has_wedding = await con.fetchval(f'''select exists(select 1 from weddings where chat_id = {message.chat.id} and 
                      (user1_id = {message.from_user.id} or user2_id = {message.from_user.id}))''')
        if has_wedding:
            await message.answer(text="Ви вже одружені в цьому чаті, щоб розвестись напишіть !розійтись")
            return

        if accused_user_id == message.from_user.id:
            await message.answer(f"Не можна одружитись на самому собі")
            return
        profile = await get_profile(message.chat.id, accused_user_id, con)
    await message.answer(f'''{message.from_user.get_mention(as_html=True)} відправив {get_mention(profile['user_id'], get_nickname(profile))} пропозицію одружитись''',
                         reply_markup=get_wedding_keyboard(user1=message.from_user.id, user2=profile['user_id']))


@dp.callback_query_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), wedding_callback.filter(level="1"))
async def weddings_2(call: CallbackQuery, callback_data : dict, pool: Pool):
    if str(call.from_user.id) != callback_data['user2']:
        await call.answer(text="Ви не та людина кому робили пропозицію", show_alert=True, cache_time=1)
        return

    async with pool.acquire() as con:
        profile1 = await get_profile(call.message.chat.id, callback_data['user1'], con)
        if callback_data['to']=="no":
            await call.message.delete()
            await call.message.answer(f'''{call.from_user.get_mention()} відмовився від пропозицію, співчуваєм {get_mention(profile1['user_id'], get_nickname(profile1))}''')
            return

        if callback_data['to']=="yes":
            has_wedding = await con.fetchval(f'''select exists(select 1 from weddings where chat_id = {call.message.chat.id} and 
            (user1_id = {call.from_user.id} or user2_id = {call.from_user.id}))''')

            if has_wedding:
                await call.answer(text="Ви вже одружені в цьому чаті, щоб розвестись напишіть !розійтись", show_alert=True, cache_time=1)
                return

            await con.execute(f'''insert into weddings(chat_id, user1_id, user2_id, datetime) values ({call.message.chat.id}, 
            {callback_data['user1']}, {callback_data['user2']}, '{(datetime.datetime.now() + time_delta).strftime("%Y-%m-%d %H:%M:%S")}'::timestamp)''')
            await call.message.answer(f'''{call.from_user.get_mention()} прийняла пропозицію від {get_mention(profile1['user_id'], get_nickname(profile1))}, вітаємо молодих 🥳🥳🥳''')
            await call.message.edit_reply_markup()


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"розійтись"))
async def divorce_1(message: Message, pool: Pool):
    async with pool.acquire() as con:
        has_wedding = await con.fetchval(f'''select exists(select 1 from weddings where chat_id = {message.chat.id} and 
                    (user1_id = {message.from_user.id} or user2_id = {message.from_user.id}))''')
        if not has_wedding:
            await message.answer(f"Ви не одружені")
            return

        await message.answer(f'Вы впевнені, що хочете розійтись?', reply_markup=get_divorce_keyboard(message.from_user.id))


@dp.callback_query_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), wedding_callback.filter(level="-1"))
async def divorce_2(call: CallbackQuery, callback_data : dict, pool: Pool):
    if str(call.from_user.id) != callback_data['user1']:
        await call.answer(text="Выи не та людина, яка хоче розійтись", show_alert=True, cache_time=1)
        return

    async with pool.acquire() as con:
        if callback_data['to']=="no":
            await call.message.edit_reply_markup()
            return

        if callback_data['to']=="yes":
            await con.execute(f'''delete from weddings where chat_id = {call.message.chat.id} and 
                    (user1_id = {call.from_user.id} or user2_id = {call.from_user.id})''')

            await call.message.answer(f'{call.from_user.get_mention()}, ви успішно розійшлись')
            await call.message.delete()



