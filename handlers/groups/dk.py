import re

from aiogram.dispatcher.filters import ChatTypeFilter, IsReplyFilter, Regexp
from aiogram.types import ChatType, Message
from asyncpg import Pool

from loader import dp, prefixes, ranks, commands_id, ranks_normal_dict, interval_available
from utils.dop_func import get_mention, get_nickname, get_interval_from_str, get_user_id, check_if_has_permission, \
    get_profile
from utils.my_exceptions import ProfileNotFound, NotEnoughRank


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), Regexp(r"(?is)^" + prefixes + fr"дк\s+(?P<name_of_command>.+)(\s+(?P<rank>\d+))"))
async def dk(message: Message, pool: Pool):
    match = re.search(r"(?is)^" + prefixes + fr"дк\s+(?P<name_of_command>.+)(\s+(?P<rank>\d+))", message.text)
    d = match.groupdict()

    await check_if_has_permission(chat_id=message.chat.id, moderator_user_id=message.from_user.id, pool=pool, command_name="встановлення доступу команд")
    if int(d['rank']) not in ranks.keys():
        await message.answer(f"Ранг може бути від 0 ({ranks[0].capitalize()}) до 4 ({ranks[4].capitalize()})")
        return

    if not commands_id.get(d['name_of_command']):
        await message.answer(f"Не зміг найти цю команду")
        return

    async with pool.acquire() as con:
        await con.execute(f'''update commands set rank = {d['rank']} where chat_id = {message.chat.id} and command_id = {commands_id[d['name_of_command']]}''')

    await message.answer(f'''Команда «{d['name_of_command'].capitalize()}» теперь доступна з рангу {ranks[int(d['rank'])].capitalize()} ({d['rank']})''')


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), Regexp(r"(?is)^" + prefixes + fr"хто\s+адмін"))
async def dk(message: Message, pool: Pool):
    text = "Адміни групи:\n\n"

    async with pool.acquire() as con:
        for rank, rank_name in ranks_normal_dict.items().__reversed__():
            if rank == 0:
                continue

            admins = await con.fetch(f'''select profiles.* from users inner join profiles on profiles.user_id = users.user_id where chat_id = {message.chat.id} and rank = {rank}
            and profiles.user_id <> {dp.bot.id}''')

            if not admins:
                continue

            text += rank_name.upper() + "\n"
            for admin in admins:
                text += f"👤 {get_mention(admin['user_id'], get_nickname(admin))}\n"
            text+="\n"

    await message.answer(text)



@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"адмін[. ,!;]+(?P<rank>\d+)\s+@(?P<link>[\w\d]+)"))
@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),IsReplyFilter(is_reply=True), Regexp(r"(?is)^" + prefixes + fr"адмін[. ,!;]+(?P<rank>\d+)"))
async def ban_someone(message: Message, pool: Pool, regexp):


    d = regexp.groupdict()
    if message.reply_to_message:
        d['link'] = str(message.reply_to_message.from_user.id)

    async with pool.acquire() as con:
        accused_user_id = await get_user_id(d['link'], con)

        moderator = await con.fetchrow(f'''select users.rank, profiles.* from users inner join profiles on profiles.user_id = users.user_id 
        where users.chat_id = {message.chat.id} and users.user_id = {message.from_user.id}''')
        user = await con.fetchrow(f'''select users.rank, profiles.* from users inner join profiles on profiles.user_id = users.user_id 
        where users.chat_id = {message.chat.id} and users.user_id = {accused_user_id}''')
        if not user or not moderator:
            raise ProfileNotFound()

        if moderator['rank']<user['rank'] or int(d['rank'])>=moderator['rank']:
            await message.answer(f'''Помилка: адмін не може підвищити учасника до свого рангу або ранг адміна менше чим в учасника''')
            return

        await con.execute(f'''update users set rank = {d['rank']} where chat_id = {message.chat.id} and user_id = {accused_user_id}'''.replace("'None'", "null"))
        profile = await get_profile(message.chat.id, accused_user_id, con)

    await message.answer(f'''
✅ {get_mention(profile['user_id'], get_nickname(profile))} назначений {ranks[int(d['rank'])]} [{d['rank']}]''')


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"розжалувати\s+@(?P<link>[\w\d]+)"))
@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),IsReplyFilter(is_reply=True), Regexp(r"(?is)^" + prefixes + fr"розжалувати"))
async def ban_someone(message: Message, pool: Pool, regexp):

    d = regexp.groupdict()
    if message.reply_to_message:
        d['link'] = str(message.reply_to_message.from_user.id)

    async with pool.acquire() as con:
        accused_user_id = await get_user_id(d['link'], con)

        moderator = await con.fetchrow(f'''select users.rank, profiles.* from users inner join profiles on profiles.user_id = users.user_id 
        where users.chat_id = {message.chat.id} and users.user_id = {message.from_user.id}''')
        user = await con.fetchrow(f'''select users.rank, profiles.* from users inner join profiles on profiles.user_id = users.user_id 
        where users.chat_id = {message.chat.id} and users.user_id = {accused_user_id}''')

        if not user or not moderator:
            raise ProfileNotFound()

        if moderator['rank']<=user['rank']:
            await message.answer(f'''Помилка: адмін не може розжалуваний учасника до свого рангу або ранг адміну менше чем учасника''')
            return

        await con.execute(f'''update users set rank = 0 where chat_id = {message.chat.id} and user_id = {accused_user_id}'''.replace("'None'", "null"))
        profile = await get_profile(message.chat.id, accused_user_id, con)

    await message.answer(f'''
✅ {get_mention(profile['user_id'], get_nickname(profile))} був розжалуваний до рангу {ranks[0]} [{0}]''')



@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^!передати\s+власника\s+@(?P<link>[\w\d]+)"))
@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),IsReplyFilter(is_reply=True), Regexp(r"(?is)^!передати\s+власника"))
async def give_owner(message: Message, pool: Pool, regexp):

    d = regexp.groupdict()
    if message.reply_to_message:
        d['link'] = str(message.reply_to_message.from_user.id)

    async with pool.acquire() as con:
        moderator_rank = await con.fetchval(f'''select rank from users where chat_id = {message.chat.id} and user_id = {message.from_user.id}''')
        if moderator_rank !=4:
            await message.answer(f'''Передати права власника може тільки власник''')
            return

        accused_user_id = await get_user_id(d['link'], con)

        await con.execute(f'''update users set rank = 4 where chat_id = {message.chat.id} and user_id = {accused_user_id}''')
        await con.execute(f'''update users set rank = 3 where chat_id = {message.chat.id} and user_id = {message.from_user.id}''')
        await con.execute(f'''update groups set is_transfer_owner = false, prev_owner_user_id = {message.from_user.id} where chat_id = {message.chat.id}''')

        profile = await get_profile(message.chat.id, accused_user_id, con)

    await message.answer(f'''✅Права власника успішно передані користувачу {get_mention(profile['user_id'], get_nickname(profile))}''')



@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"повернення\s+власника"))
async def give_owner(message: Message, pool: Pool):
    async with pool.acquire() as con:
        is_transfer_owner = await con.fetchval(f'''select is_transfer_owner from groups where chat_id = {message.chat.id}''')
        if not is_transfer_owner:
            await message.answer("Повернення власника відключено, щоб включити власник має написати команду +повернення власника")
            return
        prev_owner_user_id = await con.fetchval(f'''select prev_owner_user_id from groups where chat_id = {message.chat.id}''')

        current_tg_owner_user_id = None
        admins = await message.chat.get_administrators()
        for admin in admins:
            if admin.is_chat_owner:
                current_tg_owner_user_id = admin.user.id

        if message.from_user.id not in [prev_owner_user_id, current_tg_owner_user_id]:
            await message.answer(f'''Тільки творець чату може вернуту власника собі''')
            return

        await con.execute(f'''update users set rank = 1 where chat_id = {message.chat.id} and rank = 4''')
        await con.execute(f'''update users set rank = 4 where chat_id = {message.chat.id} and user_id = {message.from_user.id}''')
        await con.execute(f'''update groups set is_transfer_owner = false, owner_user_id = {message.from_user.id} where chat_id = {message.chat.id}''')

    await message.answer(f'''✅ Творець бесіди повернув собі свої права''')


