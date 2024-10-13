import html
import logging

from aiogram import types
from aiogram.dispatcher.handler import ctx_data, CancelHandler
from aiogram.utils.exceptions import BotKicked, BadRequest, NotEnoughRightsToRestrict, CantRestrictChatOwner, \
    UserIsAnAdministratorOfTheChat, CantRestrictSelf, CantDemoteChatCreator

from filters import ManyExceptionsFilter
from loader import dp, exceptions_chat_id, commands_id, ranks


from utils.my_exceptions import ProfileNotFound, NotEnoughRank


@dp.errors_handler(exception=CantRestrictSelf)
async def errors_handler(update, exception):
    if update.callback_query:
        chat_id = update.callback_query.message.chat.id
    elif update.message:
        chat_id= update.message.chat.id
    await dp.bot.send_message(chat_id=chat_id, text=f'''вибачай, себе забанити не можу(''')
    return True


@dp.errors_handler(ManyExceptionsFilter([NotEnoughRightsToRestrict, CantRestrictChatOwner, UserIsAnAdministratorOfTheChat, CantRestrictSelf, CantDemoteChatCreator]))
async def errors_handler(update, exception):
    if update.callback_query:
        chat_id = update.callback_query.message.chat.id
    elif update.message:
        chat_id= update.message.chat.id
    await dp.bot.send_message(chat_id=chat_id, text=f'''⚠️ Не вдалося виконати команду\nПомилка: Недостатньо прав для даної дії''')
    return True


@dp.errors_handler(exception=BadRequest)
async def errors_handler(update, exception, pool):
    if update.callback_query:
        user = update.callback_query.from_user
        chat_id = update.callback_query.message.chat.id
    elif update.message:
        user = update.message.from_user
        chat_id= update.message.chat.id
    else:
        logging.exception(f'Update: {update} \n{exception}')
        return True

    if f"{exception}"=="Not enough rights to send text messages to the chat":
            async with pool.acquire() as con:
                await con.execute(f'''update groups set can_send_messages = false where chat_id = {chat_id}''')

    if chat_id:
        try:
            text = f'Чат менеджер виникла помилка у {user.get_mention(as_html=True)}:\n\n{html.escape(exception.__str__())}\n\n{html.escape(update.__str__())}'
            await dp.bot.send_message(chat_id=exceptions_chat_id, text=text[:3800])
        except Exception as exc:
            logging.exception(exc)
    try:
        await dp.bot.send_message(chat_id=chat_id, text=f'''
⚠️ Не вдалось виконати команду
Помилка ТГ: {html.escape(exception.__str__())}''')
    except Exception as exc:
        return True

    return True


@dp.errors_handler(exception=ProfileNotFound)
async def errors_handler(update, exception : ProfileNotFound):
    if update.callback_query:
        chat_id = update.callback_query.message.chat.id
    elif update.message:
        chat_id= update.message.chat.id
    await dp.bot.send_message(chat_id=chat_id, text="Помилка, учасник не був знайдений")
    return True


@dp.errors_handler(exception=NotEnoughRank)
async def errors_handler(update, exception : NotEnoughRank):
    if update.callback_query:
        chat_id = update.callback_query.message.chat.id
    elif update.message:
        chat_id= update.message.chat.id

    await dp.bot.send_message(chat_id=chat_id, text=
    f"Помилка, у вас недостатньо прав або ранг менший\n"
    f"📝 Команда доступна тільки з рангу {ranks[exception.rank_required].capitalize()} ({exception.rank_required})\n"
    f"Обмеження: Команда «{commands_id[exception.command_id].capitalize()}» ({exception.command_id})")
    raise CancelHandler


@dp.errors_handler()
async def errors_hand(update:types.Update, exception :KeyError, pool):

    chat_id = None

    state = dp.current_state()
    await state.reset_state(with_data=True)

    if update.callback_query:
        user = update.callback_query.from_user
        chat_id = update.callback_query.message.chat.id
    elif update.message:
        user = update.message.from_user
        chat_id= update.message.chat.id

    if f"{exception}"=="Not enough rights to send text messages to the chat":
        async with pool.acquire() as con:
            await con.execute(f'''update groups set can_send_messages = false where chat_id = {chat_id}''')

    if chat_id:
        try:
            text = f'Чат менеджер виникла помилка у {user.get_mention(as_html=True)}:\n\n{html.escape(exception.__str__())}\n\n{html.escape(update.__str__())}'
            await dp.bot.send_message(chat_id=exceptions_chat_id, text=text[:3800])
        except Exception as exc:
            logging.exception(exc)

    logging.exception(f'Update: {update} \n{exception}')
    return True

# @dp.errors_handler()
# async def errors_handler(update, exception):
#     """
#     Exceptions handler. Catches all exceptions within task factory tasks.
#     :param update:
#     :param exception:
#     :return: stdout logging
#     """
#     from aiogram.utils.exceptions import (Unauthorized, InvalidQueryID, TelegramAPIError,
#                                           CantDemoteChatCreator, MessageNotModified, MessageToDeleteNotFound,
#                                           MessageTextIsEmpty, RetryAfter,
#                                           CantParseEntities, MessageCantBeDeleted, BadRequest)
#
#     if isinstance(exception, CantDemoteChatCreator):
#         logging.debug("Can't demote chat creator")
#         return True
#
#     if isinstance(exception, MessageNotModified):
#         logging.debug('Message is not modified')
#         return True
#     if isinstance(exception, MessageCantBeDeleted):
#         logging.debug('Message cant be deleted')
#         return True
#
#     if isinstance(exception, MessageToDeleteNotFound):
#         logging.debug('Message to delete not found')
#         return True
#
#     if isinstance(exception, MessageTextIsEmpty):
#         logging.debug('MessageTextIsEmpty')
#         return True
#
#     if isinstance(exception, Unauthorized):
#         logging.info(f'Unauthorized: {exception}')
#         return True
#
#     if isinstance(exception, InvalidQueryID):
#         logging.exception(f'InvalidQueryID: {exception} \nUpdate: {update}')
#         return True
#
#     if isinstance(exception, TelegramAPIError):
#         logging.exception(f'TelegramAPIError: {exception} \nUpdate: {update}')
#         return True
#     if isinstance(exception, RetryAfter):
#         logging.exception(f'RetryAfter: {exception} \nUpdate: {update}')
#         return True
#     if isinstance(exception, CantParseEntities):
#         logging.exception(f'CantParseEntities: {exception} \nUpdate: {update}')
#         return True
#     if isinstance(exception, BadRequest):
#         logging.exception(f'CantParseEntities: {exception} \nUpdate: {update}')
#         return True
#     logging.exception(f'Update: {update} \n{exception}')
