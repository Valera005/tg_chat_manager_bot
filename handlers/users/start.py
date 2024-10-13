import html
import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart, ChatTypeFilter
from aiogram.types import ChatType, MessageEntityType
from asyncpg import Pool, UniqueViolationError

from keyboards.inline.start_keyboard import start_keyboard
from loader import dp, name_of_bot


@dp.message_handler(CommandStart(), ChatTypeFilter([ChatType.PRIVATE]), state='*')
async def bot_start(message: types.Message, pool : Pool, state : FSMContext):
    await state.reset_state()
    async with pool.acquire() as con:
        args = message.get_args()

        if args:
            await con.execute(f'''update links set number_of_trans = number_of_trans+1 where deeplink = '{args}' ''')
        await con.execute(f'''insert into users_private(chat_id, user_id, username, first_name, full_name, deeplink, datetime) values
                                        ({message.chat.id}, {message.from_user.id}, '{message.from_user.username}', '{message.from_user.first_name.replace("'", "''")}',
                                         '{message.from_user.full_name.replace("'", "''")}',  '{args if args else None}', '{message.date.strftime("%Y-%m-%d %H:%M:%S")}'::timestamp) on conflict do nothing'''.replace("'None'", "null"))

        await con.execute(f'''insert into profiles(user_id, username, first_name, full_name) values
                                                           ({message.from_user.id}, '{message.from_user.username}', '{message.from_user.first_name.replace("'", "''")}',
                                                          '{message.from_user.full_name.replace("'", "''")}') on conflict do nothing'''.replace("'None'", "null"))
    await message.answer(f'''
Привіт, додавай мене в чат
''', reply_markup=start_keyboard)



@dp.message_handler(CommandStart(),  ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), state='*')
async def bot_start_group(message: types.Message, pool : Pool, state : FSMContext):
    await state.reset_state()

    async with pool.acquire() as con:
        chat = message.chat
        await con.execute(f'''Insert into groups(chat_id, title, username, type, chat_member_type, date_of_addition, date_of_edit) values 
                        ({chat.id}, '{chat.title.replace("'", "''")}', '{chat.username}', '{chat.type}', 'member', 
                        '{message.date.strftime("%Y-%m-%d %H:%M:%S")}'::timestamp, '{message.date.strftime("%Y-%m-%d %H:%M:%S")}'::timestamp)'''.replace(
                "'None'", "null"))


    await message.answer(f'''
Всім привіт
''', disable_web_page_preview=True)
