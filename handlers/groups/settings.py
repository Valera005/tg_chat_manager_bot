from aiogram.dispatcher.filters import ChatTypeFilter, Regexp
from aiogram.types import ChatType, Message
from asyncpg import Pool

from loader import dp, prefixes
from utils.dop_func import check_if_has_permission


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^[+-]бесіди"))
async def divorce_1(message: Message, pool: Pool):
    await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool=pool, command_name="налаштування")
    async with pool.acquire() as con:
        await con.execute(f'''update groups set is_talks = {"true" if message.text[0]=="+" else "false"}''')
    await message.answer(f'''Посилання на бесіди були успішно {"включені" if message.text[0]=="+" else "виключені"}''')


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^[+-]сайти"))
async def divorce_1(message: Message, pool: Pool):
    await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool=pool, command_name="налаштування")
    async with pool.acquire() as con:
        await con.execute(f'''update groups set is_urls = {"true" if message.text[0]=="+" else "false"}''')
    await message.answer(f'''Посилання на сторонні сайти були успішно {"включені" if message.text[0]=="+" else "виключені"}''')


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^[+-]групи"))
async def divorce_1(message: Message, pool: Pool):
    await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool=pool, command_name="налаштування")
    async with pool.acquire() as con:
        await con.execute(f'''update groups set is_groups = {"true" if message.text[0]=="+" else "false"}''')
    await message.answer(f'''Посилання на сторонні групи були успішно {"включені" if message.text[0]=="+" else "виключені"}''')


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^[+-]боти"))
async def divorce_1(message: Message, pool: Pool):
    await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool=pool, command_name="налаштування")
    async with pool.acquire() as con:
        await con.execute(f'''update groups set is_bots = {"true" if message.text[0]=="+" else "false"}''')
    await message.answer(f'''Запрошення ботів були успішно {"включені" if message.text[0]=="+" else "виключені"}''')


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^[+-]канали"))
async def divorce_1(message: Message, pool: Pool):
    await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool=pool, command_name="налаштування")
    async with pool.acquire() as con:
        await con.execute(f'''update groups set is_channels = {"true" if message.text[0]=="+" else "false"}''')
    await message.answer(f'''Посилання на сторонні канали були успішно {"включені" if message.text[0]=="+" else "виключені"}''')


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^[+-](повернення)\s+власника"))
async def divorce_1(message: Message, pool: Pool):

    async with pool.acquire() as con:
        rank = await con.fetchval(f'''select rank from users where chat_id = {message.chat.id} and user_id = {message.from_user.id}''')
        if rank!=4:
            await message.answer(f'''Тільки власник може викликати дану команду''')
            return
        await con.execute(f'''update groups set is_transfer_owner = {"true" if message.text[0]=="+" else "false"}''')
    await message.answer(f'''Повернення власника успішно {"включені" if message.text[0]=="+" else "виключено"}''')