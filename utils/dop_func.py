import html
import re

import asyncpg
from aiogram.dispatcher.handler import ctx_data
from aiogram.types import Message
from asyncpg import Pool

from loader import interval_dict, morph, commands_id
from utils.my_exceptions import ProfileNotFound, NotEnoughRank


def get_mention(user_id, text):
    return f"<a href='tg://user?id={user_id}'>{html.escape(text)}</a>"

def get_nickname(profile : dict):
    return profile.get('nickname') if profile.get('nickname') else profile['full_name']


def get_interval_from_str(string : str):
    match = re.match("(?i)(?P<number>\d+)\s+(?P<interval>.+)", string)
    d = match.groupdict()

    return f"{d['number']} {interval_dict[morph.parse(d['interval'])[0][2]]}"

async def get_user_id(link : str, con):
    try:
        return int(link)
    except ValueError:
        user_id = await con.fetchval(f"select user_id from profiles where username = '{link.replace('@','')}'")
        if not user_id:
            raise ProfileNotFound()
        return user_id


def get_key_by_value(my_dict : dict, value):
    return [key for key in my_dict if my_dict[key]==value][0]


async def check_if_has_permission(chat_id, moderator_user_id, command_name, pool : Pool, accused_user_id = None):

    command_id = commands_id[command_name]

    if accused_user_id is None:
        data = await pool.fetchrow(f'''select 
        (select rank from users where user_id = {moderator_user_id} and chat_id = {chat_id})>=
        (select rank from commands where chat_id = {chat_id} and command_id = {command_id}) as answer, 
        rank as rank_required, command_id from commands where chat_id = {chat_id} and command_id = {command_id}''')

        if not data['answer']:
            raise NotEnoughRank(rank_required=data['rank_required'], command_id= data['command_id'])

        return

    else:

        data = await pool.fetchrow(f'''select 
        (select rank from users where user_id = {moderator_user_id} and chat_id = {chat_id})>=
        (select rank from commands where chat_id = {chat_id} and command_id = {command_id}) and 
        (select rank from users where user_id = {moderator_user_id} and chat_id = {chat_id})>
        (select rank from users where user_id = {accused_user_id} and chat_id = {chat_id}) as answer, 
        rank as rank_required, command_id from commands where chat_id = {chat_id} and command_id = {command_id}''')

        if not data['answer']:
            raise NotEnoughRank(rank_required=data['rank_required'], command_id=data['command_id'])

        return


async def get_profile(chat_id, user_id, con):
    profile = await con.fetchrow(f'''select users.nickname, profiles.* from users inner join profiles on users.user_id = profiles.user_id where users.user_id = {user_id} and users.chat_id = {chat_id}''')

    if profile is None:
        raise ProfileNotFound()

    return profile


