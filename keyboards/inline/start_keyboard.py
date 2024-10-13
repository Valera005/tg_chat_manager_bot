from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from loader import link_to_bot

start_callback = CallbackData("sta", "level", "to")

def get_start_callback(level= '', to = ''):
    return start_callback.new(level=level, to=to)

start_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Додати бота в чат", url=f"{link_to_bot}?startgroup=true&admin=change_info+pin_messages")],
])

