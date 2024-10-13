import datetime
import random

from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import ChatMemberUpdated, ContentTypes, Message, ChatType
from aiogram.utils.exceptions import Unauthorized, MessageCantBeForwarded, BadRequest
from asyncpg import UniqueViolationError, Pool

from data.config import time_delta
from loader import dp, commands_id
from utils.migration_class import migration

# @dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]))
# async def new_chat_member(message : Message, pool : Pool):
#     print(message.html_text)
#     print(message.entities)



@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), content_types=ContentTypes.NEW_CHAT_MEMBERS)
async def new_chat_member(message : Message, pool : Pool):
    async with pool.acquire() as con:
        group_info = await con.fetchrow(f'''select max_invites, is_bots from groups where chat_id = {message.chat.id}''')
        max_invites = group_info['max_invites']
        is_bots = group_info['is_bots']

        interval_ban = datetime.timedelta(minutes=1)

        if max_invites != 0 and len(message.new_chat_members)>max_invites:
            members_to_ban = message.new_chat_members[max_invites:]
            for member_to_ban in members_to_ban:
                try:
                    await dp.bot.ban_chat_member(chat_id=message.chat.id, user_id=member_to_ban.id, until_date=interval_ban)
                except BadRequest:
                    pass

            await message.answer(f"Максимальна кільксть запрошених за 1 раз користувачів дорівнює {max_invites}\n\n"
                                 f"Последние {len(members_to_ban)} были кикнуты автоматически")

        for member in message.new_chat_members:
            await con.execute(f'''delete from bans where chat_id = {message.chat.id} and user_id = {member.id}''')

            if member.is_bot and not is_bots:
                try:
                    await dp.bot.ban_chat_member(chat_id=message.chat.id, user_id=member.id,until_date=interval_ban)
                    await message.answer(f"Не можна запрошувати ботів в групу, {member.get_mention()} був кікнутий, щоб виключити це обмеження, введіть +боти")
                except BadRequest:
                    await message.answer(f"Не вдалось кікнуть {member.get_mention()}")
                    pass


            try:
                await con.execute(f'''insert into users(chat_id, user_id, datetime, invited_by_user_id) values
                ({message.chat.id}, {member.id}, '{(datetime.datetime.now() + time_delta).strftime("%Y-%m-%d %H:%M:%S")}'::timestamp,
                {message.from_user.id}) '''.replace("'None'", "null"))
            except UniqueViolationError:
                pass

            try:
                await con.execute(f'''insert into profiles(user_id, username, first_name, full_name) values
                ({member.id}, '{member.username}', '{member.first_name.replace("'", "''")}',
                 '{member.full_name.replace("'", "''")}') '''.replace("'None'","null"))
            except UniqueViolationError:
                pass

        hello_message : str = await con.fetchval(f'''select hello_message from groups where chat_id = {message.chat.id}''')

    if hello_message and len(message.new_chat_members)==1:
        await message.answer(hello_message.replace("{имя}",message.new_chat_members[0].get_mention(as_html=True)))
    elif hello_message:
        await message.answer("Привіт всім новеньким)")


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), content_types=ContentTypes.LEFT_CHAT_MEMBER)
async def left_chat_member(message : Message, pool : Pool):
    async with pool.acquire() as con:
        user_left = message.left_chat_member
        owner_user_id = await con.fetchval(f'''select owner_user_id from groups where chat_id = {message.chat.id}''')

        if user_left.id == owner_user_id:
            admins = await message.chat.get_administrators()

            new_owner_user_id = None
            for admin in admins:
                if admin.is_chat_creator():
                    new_owner_user_id = admin.user.id

            await con.execute(f'''update groups set is_transfer_owner = true, prev_owner_user_id = {owner_user_id}, owner_user_id = {new_owner_user_id} where chat_id = {message.chat.id}''')

        await con.execute(f'''delete from users where chat_id = {message.chat.id} and user_id = {message.left_chat_member.id}''')


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), content_types=ContentTypes.MIGRATE_FROM_CHAT_ID)
async def migrate_chat(message : Message, pool : Pool):
    migration.add_migrate_from_chat_id(message.migrate_from_chat_id)
    await migration.check_migration(pool)


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), content_types=ContentTypes.MIGRATE_TO_CHAT_ID)
async def migrate_chat(message : Message, pool : Pool):
    migration.add_migrate_to_chat_id(message.migrate_to_chat_id)
    await migration.check_migration(pool)


@dp.my_chat_member_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]))
async def me_add_to_group(chat_member_updated: ChatMemberUpdated,  pool : Pool):

    try:
        if chat_member_updated.new_chat_member.status=="left":
            return
            #await dp.bot.send_message(chat_id=chat_member_updated.from_user.id, text="Очень жаль, что мы завершаем наше общение")
    except Unauthorized:
        pass


    chat = chat_member_updated.chat

    async with pool.acquire() as con:
        admins = await chat.get_administrators()

        owner_user_id = None
        for admin in admins:
            try:
                if admin.is_chat_creator():
                    owner_user_id = admin.user.id
                    await con.execute(f'''insert into users(chat_id,user_id, rank, datetime) values({chat.id}, {admin.user.id} , 4,
                    '{(datetime.datetime.now() + time_delta).strftime("%Y-%m-%d %H:%M:%S")}'::timestamp)''')
                else:
                    await con.execute(f'''insert into users(chat_id,user_id, rank, datetime) values({chat.id}, {admin.user.id} , 1, 
                    '{(datetime.datetime.now() + time_delta).strftime("%Y-%m-%d %H:%M:%S")}'::timestamp)''')
            except UniqueViolationError:
                pass


        try:
            await con.execute(f'''Insert into groups(chat_id, title, username, type, chat_member_type, date_of_addition, date_of_edit, owner_user_id) values 
                ({chat.id}, '{chat.title.replace("'", "''") if chat.title else None}', '{chat.username}', '{chat.type}', '{chat_member_updated.new_chat_member.status}', 
                '{(chat_member_updated.date + time_delta).strftime("%Y-%m-%d %H:%M:%S")}'::timestamp, '{(chat_member_updated.date + time_delta).strftime("%Y-%m-%d %H:%M:%S")}'::timestamp, 
                {owner_user_id if owner_user_id else "'None'"})'''.replace("'None'", "null"))
        except UniqueViolationError:
            await con.execute(f'''Update groups set can_send_messages = true, chat_member_type = '{chat_member_updated.new_chat_member.status}', date_of_edit = '{chat_member_updated.date.strftime("%Y-%m-%d %H:%M:%S")}'::timestamp where chat_id = {chat.id}''')

        sql = f'''insert into commands(chat_id, command_id, rank) values'''
        for command_id in range(1,101):
            sql+= f" ({chat.id}, {command_id}, 1),"

        sql += f" ({chat.id}, 1000, 4),"
        sql = sql[:-1]
        sql += " ON CONFLICT(chat_id, command_id) DO NOTHING"
        try:
            await con.execute(sql)
        except UniqueViolationError:
            pass






