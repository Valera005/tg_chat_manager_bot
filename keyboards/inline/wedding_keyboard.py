from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

wedding_callback = CallbackData("wed","level","to", "user1","user2")

my_profile_callback = CallbackData("mpro","level","to", "user_id")


def get_wedding_callback(level = '', to = '', user1= '', user2=''):
    return wedding_callback.new(level=level, to=to, user1 = user1, user2 = user2)

def get_my_profile_callback(level = '', to = '', user_id= ''):
    return my_profile_callback.new(level=level, to=to, user_id = user_id)

def get_my_profile_keyboard(user_id):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏆Мої нагороди",callback_data=get_my_profile_callback(level="1", to="rewards", user_id = user_id))],
    ])
    return markup


def get_wedding_keyboard(user1, user2):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Погодитися", callback_data= get_wedding_callback(level= "1", to="yes",user1=user1, user2 = user2))],
        [InlineKeyboardButton(text="Відмовити", callback_data= get_wedding_callback(level= "1", to="no",user1=user1, user2 = user2))]
    ])

    return markup



def get_divorce_keyboard(user1):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Так, розвестись",callback_data= get_wedding_callback( level="-1", to="yes",user1=user1))],
        [InlineKeyboardButton(text="Нет", callback_data= get_wedding_callback( level="-1", to="no", user1=user1))]
    ])

    return markup