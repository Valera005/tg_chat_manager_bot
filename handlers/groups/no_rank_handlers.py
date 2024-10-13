import random
import re

from aiogram.dispatcher.filters import Regexp, ChatTypeFilter, IsReplyFilter
from aiogram.types import Message, ChatType, CallbackQuery
from asyncpg import Pool

from keyboards.inline.wedding_keyboard import get_my_profile_callback, get_my_profile_keyboard, my_profile_callback
from loader import prefixes, dp, commands_dict, commands_normal_dict, link_to_bot
from utils.dop_func import get_mention, get_nickname, get_user_id, get_profile
from utils.my_exceptions import ProfileNotFound


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"хто\s+я"))
async def top_active(message: Message, pool: Pool):
    async with pool.acquire() as con:
        data = await con.fetchrow(f'''select profiles.*, users.karma, users.nickname,
        (select count(1) from messages where user_id = {message.from_user.id} and chat_id = {message.chat.id} and current_date - datetime::date <= 7) as num_of_messages_week,
        (select count(1) from messages where user_id = {message.from_user.id} and chat_id = {message.chat.id} and datetime::date = current_date) as num_of_messages_day
        from profiles inner join users on users.user_id = profiles.user_id and users.chat_id = {message.chat.id}  
        where profiles.user_id = {message.from_user.id}''')



        text = f'''{get_mention(data['user_id'], get_nickname(data))}

Твоя репутація: {data['karma']}
Твій актив за сьогодні: {data['num_of_messages_day']} повідомлень
Твій актив за тиждень: {data['num_of_messages_week']} повідомлень\n'''

        wedding_info = await con.fetchrow(f'''select * from weddings where chat_id = {message.chat.id} and (user1_id = {message.from_user.id}  or  user2_id = {message.from_user.id})''')

        if wedding_info:
            pair_user_id = wedding_info['user1_id'] if wedding_info['user1_id'] != message.from_user.id else wedding_info['user2_id']
            pair_profile = await get_profile(message.chat.id, pair_user_id, con)
            text+=f"Брак: {get_mention(pair_profile['user_id'], get_nickname(pair_profile))}"
        else:
            text+=f"Брак: одинак"

    await message.answer(text, reply_markup=get_my_profile_keyboard(message.from_user.id))

@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), Regexp(r"(?is)^"+prefixes+r"?правила"))
async def get_rules(message : Message, pool : Pool):
    async with pool.acquire() as con:
        rules = await con.fetchval(f'''select rules from groups where chat_id = {message.chat.id}''')

    if not rules:
        await message.answer(f"📝 Правила чату поки не задані.")
        return

    await message.answer(f"🗓 Правила чату:\n{rules}")


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), Regexp(r"(?is)^"+prefixes+fr"(привітай|вітання|привіт)\s+@(?P<link>.+)"))
async def del_rules(message : Message, pool : Pool, regexp : re.Match):
    link = regexp.group("link")
    async with pool.acquire() as con:
        user_id = get_user_id(link, con)
        hello_message: str = await con.fetchval(f'''select hello_message from groups where chat_id = {message.chat.id}''')

        if not hello_message:
            await message.answer("🗓 Вітання чату пока не встановлено")
            return

        try:
            profile = await get_profile(message.chat.id, user_id, con)
        except ProfileNotFound:
            await message.answer("🗓 Вітання чату:\n" + hello_message.replace("{имя}", message.from_user.get_mention()))
            return


    await message.answer(f"🗓 Вітання чату:\n"+hello_message.replace("{нейм}", get_mention(profile['user_id'], profile['full_name'])))



@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), Regexp(r"(?is)^"+prefixes+fr"можливість[. ,!;]+що[. ,!;]+(?P<text>.+)"))
async def del_rules(message : Message, pool : Pool, regexp):
    text = regexp.group("text")

    await message.answer(f"Можливість що {text} є {random.randint(0, 100)}%")


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), Regexp(r"(?is)^"+prefixes+fr"хто[. ,!;]+(?P<text>.+)"))
async def del_rules(message : Message, pool : Pool, regexp):
    text = regexp.group("text")

    async with pool.acquire() as con:
        profile = await con.fetchrow(f"select profiles.* from users inner join profiles on users.user_id = profiles.user_id where chat_id = {message.chat.id} order by random() limit 1")

    await message.answer(f"{get_mention(profile['user_id'], get_nickname(profile))} {text}")


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"нік[. ,!;]+(?P<nickname>.+)"))
async def top_active(message: Message, pool: Pool, regexp):

    nickname = regexp.group("nickname")
    async with pool.acquire() as con:
        await con.execute(f'''update users set nickname = '{nickname.replace("'","''")}' where chat_id = {message.chat.id} and user_id = {message.from_user.id}''')
        profile = await get_profile(message.chat.id, message.from_user.id, con)
    await message.answer(f"Тепер буду звертатись до тебе так: {get_mention(profile['user_id'], get_nickname(profile))}")



@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),IsReplyFilter(is_reply=True), lambda x: x.text.lower() in ["згоден","+"])
async def add_karma(message: Message, pool: Pool, reply : Message):
    if message.from_user.id == reply.from_user.id:
        await message.answer("Сам себе не похвалиш, ніхто не похвалить 😁")
        return

    async with pool.acquire() as con:
        karma = await con.fetchval(f'''update users set karma = karma + 1 where chat_id = {message.chat.id} and user_id = {message.reply_to_message.from_user.id} returning karma ''')

    await message.reply(f"Карма {reply.from_user.get_mention()} збільшена\nПоточне значення: {karma}")


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), IsReplyFilter(is_reply=True),lambda x: x.text.lower() in ["-"])
async def add_karma(message: Message, pool: Pool, reply: Message):
    if message.from_user.id == reply.from_user.id:
        await message.answer("Самокритично")
        return

    async with pool.acquire() as con:
        karma = await con.fetchval(f'''update users set karma = karma - 1 where chat_id = {message.chat.id} and user_id = {message.reply_to_message.from_user.id} returning karma''')

    await message.answer(f"Карма {reply.from_user.get_mention()} зменшена\nПоточне значення: {karma}")


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"оновити\s+юзернейм"))
async def top_active(message: Message, pool: Pool):
    async with pool.acquire() as con:
        await con.execute(f'''update profiles set username = '{message.from_user.username if message.from_user.username else "None"}' 
        where user_id = {message.from_user.id} returning *'''.replace("'None'", "null"))
    await message.answer(f"Ваш юзернейм було оновлено в системі")


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"команди"))
async def top_active(message: Message, pool: Pool):
    await message.answer(f"Опис команд можна найти по посиланню: {link_to_bot}?start=commands")


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]),Regexp(r"(?is)^" + prefixes + fr"мої\s+нагороди"))
async def top_active(message: Message, pool: Pool):
    async with pool.acquire() as con:

        rewards = await con.fetch(f'''select rewards.*, profiles.full_name, profiles.nickname, 
                        (select full_name moderator_full_name from profiles where user_id = rewards.moderator_user_id) 
                        from rewards inner join profiles on rewards.user_id = profiles.user_id 
                        where rewards.chat_id = {message.chat.id} and rewards.user_id = {message.from_user.id} order by id limit 10''')

        if not rewards:
            await message.answer(f'''🏆 Нагород поки немає''')
            return

        text = f'''🏆 Нагороди {get_mention(rewards[0]['user_id'], get_nickname(rewards[0]))}:'''

    for ind, reward in enumerate(rewards, start=1):
        text += f'''
{ind}. {reward['description']} 
⏱ Выдана {reward['datetime'].strftime("%d.%m.%Y %H:%M")}
'''
    await message.answer(text)


@dp.callback_query_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), my_profile_callback.filter(level="1", to = "rewards"))
async def top_active(call: CallbackQuery, pool: Pool, callback_data : dict):
    if str(call.from_user.id) != callback_data['user_id']:
        await call.answer(text="Ви не можете нажати на цю кнопку", cache_time=3)
        return
    await call.answer(cache_time=3)

    async with pool.acquire() as con:

        rewards = await con.fetch(f'''select rewards.*, profiles.full_name, users.nickname, 
                        (select full_name moderator_full_name from profiles where user_id = rewards.moderator_user_id) 
                        from rewards inner join profiles on rewards.user_id = profiles.user_id inner join users on rewards.user_id = users.user_id 
                        where rewards.chat_id = {call.message.chat.id} and rewards.user_id = {call.from_user.id} order by id limit 10''')

        if not rewards:
            await call.message.answer(f'''🏆 Нагород поки немає''')
            return

        text = f'''🏆 Нагороди {get_mention(rewards[0]['user_id'], get_nickname(rewards[0]))}:'''

    for ind, reward in enumerate(rewards, start=1):
        text += f'''
{ind}. {reward['description']}
⏱ Выдана {reward['datetime'].strftime("%d.%m.%Y %H:%M")}
'''
    await call.message.answer(text)


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]), Regexp(r"(?is)^" + prefixes + fr"зняти\s+свою\s+нагороду\s+(?P<num>\d+)"))
async def warn_someone(message: Message, pool: Pool, regexp):

    d = regexp.groupdict()
    d['link'] = str(message.from_user.id)

    async with pool.acquire() as con:
        accused_user_id = message.from_user.id

        await con.execute(f'''delete from rewards where chat_id = {message.chat.id} and user_id = {accused_user_id} and id = (select id from rewards where 
        chat_id = {message.chat.id} and user_id = {accused_user_id} order by id offset ({d['num']} - 1) limit 1)''')
        profile = await get_profile(message.chat.id, accused_user_id, con)

    await message.answer(f'❎ Нагорода {d["num"]} знята з {get_mention(profile["user_id"], get_nickname(profile))}')

