import aiogram.types
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from asyncpg import Pool, UniqueViolationError

from keyboards.inline.admin_keyboards import admin_start_keyboard, admin_callback, export_keyboard, statistics_keyboard
from loader import dp, admins, filepath, link_to_bot
from states.AdminStates import AddLink, AddChannel


@dp.message_handler(commands=["admin"], state='*', chat_type="private", user_id = admins)
async def admin_panel_1(message: types.Message, state : FSMContext):
    await state.reset_state()
    await message.answer("Виберіть функцію", reply_markup=admin_start_keyboard)

@dp.callback_query_handler(admin_callback.filter(level="1", to= "back"))
async def admin_panel_2(call : CallbackQuery, callback_data: dict):
    await call.answer()
    await call.message.edit_text("Виберіть функцію", reply_markup=admin_start_keyboard)

@dp.callback_query_handler(admin_callback.filter(level="1", to = 'exp'))
async def admin_panel_2(call : CallbackQuery, callback_data: dict):
    await call.answer()
    await call.message.edit_text("Виберіть", reply_markup=export_keyboard)

@dp.callback_query_handler(admin_callback.filter(level="2", to = "group"))
@dp.callback_query_handler(admin_callback.filter(level="2", to = "user"))
async def get_data_from_db(call: CallbackQuery, callback_data : dict, pool : Pool):
    await call.answer(cache_time=2)
    text =""

    async with pool.acquire() as con:
        sql = ""
        if callback_data["to"] == "user":
            sql = "select user_id from users_private"
        elif callback_data["to"] == "group":
            sql = "select chat_id from groups where chat_member_type <> 'left' and chat_member_type <> 'kicked' and type <> 'private'"
        rows = await con.fetch(sql)
    for row in rows:
        text+=str(row[callback_data["to"]+"_id"])+"\n"

    with open(filepath+callback_data["to"]+".txt", "w") as file:
        file.write(text)
    with open(filepath+callback_data["to"]+".txt", "rb") as file:
        await call.message.answer_document(file)

#statistics
@dp.callback_query_handler(admin_callback.filter(level="1", to = 'stat'))
async def admin_panel_2(call : CallbackQuery, pool : Pool, callback_data: dict):
    await call.answer()
    async with pool.acquire() as con:
        users_private_count_today = await con.fetchval(f'''select count(1) from users_private where datetime::date = current_date''')
        users_private_count_yesterday = await con.fetchval(f'''select count(1) from users_private where datetime::date = current_date-1''')
        groups_private_count_today = await con.fetchval(f"select count(1) from groups where date_of_addition::date = current_date and chat_member_type <> 'left' and chat_member_type <> 'kicked' and type <> 'private'")
        groups_private_count_yesterday = await con.fetchval(f"select count(1) from groups where date_of_addition::date = current_date - 1 and chat_member_type <> 'left' and chat_member_type <> 'kicked' and type <> 'private'")
        profiles_count = await con.fetchval(f"select count(1) from profiles;")
        users_count = await con.fetchval(f"select count(1) from users")
        groups_count = await con.fetchval(f"select count(1) from groups where chat_member_type <> 'left' and chat_member_type <> 'kicked' and type <> 'private'")


    await call.message.edit_text(f'''
Вчора
Нові юзери (приватні чати): {users_private_count_yesterday}
Нові групи: {groups_private_count_yesterday}

Сьогодні
Нові юзери (приватні чати): {users_private_count_today}
Нові групи: {groups_private_count_today}

Загальні:
Кількість унікальних юзерів у всіх чатах: {profiles_count}
Кількість юзерів у всіх чатах: {users_count}
Кількість груп: {groups_count}''', reply_markup=statistics_keyboard)


