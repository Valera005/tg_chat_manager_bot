from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from asyncpg import Pool

admin_callback = CallbackData("admin", "level", "to", 'link_id', 'channel_id')

def get_admin_callback(level = '', to = '', link_id = '', channel_id = ''):
    return admin_callback.new(level=level,to=to, link_id=link_id, channel_id = channel_id)


admin_start_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Статистика", callback_data=get_admin_callback(level="1",to= 'stat'))],
    [InlineKeyboardButton(text="Експорт чатів", callback_data=get_admin_callback(level="1",to= 'exp'))],
])

statistics_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data=get_admin_callback(level="1",to= 'back'))],
])

export_keyboard = InlineKeyboardMarkup(inline_keyboard=[
[InlineKeyboardButton(text="Юзери (приватні чати)", callback_data=get_admin_callback(level="2",to= 'user'))],
[InlineKeyboardButton(text="Групи", callback_data=get_admin_callback(level="2",to= 'group'))],
[InlineKeyboardButton(text="Назад", callback_data=get_admin_callback(level="1",to= 'back'))],
])

add_link_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Назад", callback_data=get_admin_callback(level='1', to='links'))]
])

