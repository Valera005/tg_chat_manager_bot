from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, ChatTypeFilter
from aiogram.types import ChatType, Message, CallbackQuery

from keyboards.inline.coomands_keyboard import commands_markup, commands_callback, commands_keyboards_dict, \
    get_commands_keyboard, back_keyboard2
from loader import dp, commands_dict

@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE),state='*', commands=["commands"])
@dp.message_handler(CommandStart(deep_link='commands'), ChatTypeFilter(ChatType.PRIVATE),state='*')
async def commands_menu(message : Message, state : FSMContext):
    await state.reset_state()
    await message.answer(f"Більшість команд зі змінною {{юзернейм}} або {{посилання}} можна використовувати у відповідь на повідомлення юзера "
                         f"і не вказувати його юзернейм", reply_markup=commands_markup)

@dp.callback_query_handler(commands_callback.filter(level = "2", id="back"))
async def commands_callback_1(call : CallbackQuery, callback_data : dict):
    await call.answer()
    await call.message.edit_text(f"Більшість команд зі змінною {{юзернейм}} або {{посилання}} можна використовувати у відповідь на повідомлення юзера "
                         f"і не вказувати його юзернейм", reply_markup=commands_markup)

@dp.callback_query_handler(commands_callback.filter(level = "1"))
async def commands_callback_2(call : CallbackQuery, callback_data : dict):
    await call.answer()
    await call.message.edit_text(text="Вибери команду яка тебе цікавить",reply_markup=get_commands_keyboard(callback_data["group_id"]))

@dp.callback_query_handler(commands_callback.filter(level = "2"))
async def commands_callback_3(call : CallbackQuery, callback_data : dict):
    await call.answer()
    await call.message.edit_text(text=commands_dict[int(callback_data["id"])], reply_markup=back_keyboard2(callback_data))
