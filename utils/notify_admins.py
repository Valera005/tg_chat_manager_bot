import logging

from aiogram import Dispatcher


async def on_startup_notify(dp: Dispatcher):
    try:
        await dp.bot.send_message(698281804, "Бот запущений")

    except Exception as err:
        logging.exception(err)
