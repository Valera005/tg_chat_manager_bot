from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

commands_callback = CallbackData("coms", "level", "group_id","id")

def get_commands_callback(level = '', group_id = '', id = ''):
    return commands_callback.new(level = level, group_id=group_id, id=id)

commands_markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Команди модерування", callback_data=get_commands_callback(level="1", group_id="1"))],
    [InlineKeyboardButton(text="Загальні команди", callback_data=get_commands_callback(level="1", group_id="2"))],
])

commands_group_markup_1 = InlineKeyboardMarkup(inline_keyboard=[
[InlineKeyboardButton(text="Доступ команд", callback_data=commands_callback.new(level="2",group_id=1, id = 1)), InlineKeyboardButton(text="Хто адмін", callback_data=commands_callback.new(level="2", group_id=1, id = 2))],
[InlineKeyboardButton(text="Назначити Адміном", callback_data=commands_callback.new(level="2", group_id=1, id = 3)), InlineKeyboardButton(text="Передати власника", callback_data=commands_callback.new(level="2", group_id=1, id = 4)) ],
[InlineKeyboardButton(text="Повернути власника", callback_data=commands_callback.new(level="2", group_id=1, id = 5)), InlineKeyboardButton(text="Встановити правила чату", callback_data=commands_callback.new(level="2", group_id=1, id = 6)) ],
[InlineKeyboardButton(text="Вітання чату", callback_data=commands_callback.new(level="2", group_id=1, id = 7)), InlineKeyboardButton(text="Нагороди", callback_data=commands_callback.new(level="2", group_id=1, id = 8)) ],
[InlineKeyboardButton(text="Налаштування бесіди", callback_data=commands_callback.new(level="2", group_id=1, id = 9)), InlineKeyboardButton(text="Попереждення, варни", callback_data=commands_callback.new(level="2", group_id=1, id = 10))],
[InlineKeyboardButton(text="Бан/розбан", callback_data=commands_callback.new(level="2", group_id=1, id = 11)), InlineKeyboardButton(text="Кік", callback_data=commands_callback.new(level="2", group_id=1, id = 12))],
#[InlineKeyboardButton(text="Доступ команд", callback_data=commands_callback.new(level="2",group_id=1, id = 13))],
[InlineKeyboardButton(text="Назад", callback_data=get_commands_callback(level="2", id = "back"))]
])

commands_group_markup_2 = InlineKeyboardMarkup(inline_keyboard=[
[InlineKeyboardButton(text="Хто я", callback_data=get_commands_callback(level="2", group_id='2', id = '14')), InlineKeyboardButton(text="Правила чату", callback_data=get_commands_callback(level="2", group_id='2', id = '15'))],
[InlineKeyboardButton(text="Привітати когось", callback_data=get_commands_callback(level="2", group_id='2', id = '16')), InlineKeyboardButton(text="Можливість чогось", callback_data=get_commands_callback(level="2", group_id='2', id = '17'))],
[InlineKeyboardButton(text="Хто...", callback_data=get_commands_callback(level="2", group_id='2', id = '18')), InlineKeyboardButton(text="Нік", callback_data=get_commands_callback(level="2", group_id='2', id = '19'))],
[InlineKeyboardButton(text="Репутація", callback_data=get_commands_callback(level="2", group_id='2', id = '20')), InlineKeyboardButton(text="Топ активних", callback_data=get_commands_callback(level="2", group_id='2', id = '21'))],
[InlineKeyboardButton(text="Весілля", callback_data=get_commands_callback(level="2", group_id='2', id = '22')), InlineKeyboardButton(text="Нагороди", callback_data=get_commands_callback(level="2", group_id='2', id = '23'))],
[InlineKeyboardButton(text="Назад", callback_data=get_commands_callback(level="2", id = "back"))]
])



commands_keyboards_dict = {"1":commands_group_markup_1, "2":commands_group_markup_2}


def back_keyboard2(callback_data):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data=get_commands_callback(level= "1", group_id=callback_data['group_id']))]])

def get_commands_keyboard(group_id):
    markup = commands_keyboards_dict[group_id]
    return markup
