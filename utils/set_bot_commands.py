from aiogram import types
from aiogram.types import BotCommandScopeChat, BotCommandScopeAllPrivateChats
from aiogram.utils.exceptions import ChatNotFound

from loader import admins


async def set_default_commands(dp):
    users_scope = [
        types.BotCommand("start", "Запустити бота"),
        types.BotCommand("commands", "Команди бота")
    ]
    await dp.bot.set_my_commands(users_scope, scope=BotCommandScopeAllPrivateChats())

    for admin in admins:
        try:
            #await dp.bot.set_my_commands([types.BotCommand("admin", "Меню Админа"), types.BotCommand("admin2", "Каналы")] + users_scope, scope=BotCommandScopeChat(admin))
            await dp.bot.set_my_commands(users_scope, scope=BotCommandScopeChat(admin))
        except ChatNotFound:
            pass
