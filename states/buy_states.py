from aiogram.dispatcher.filters.state import StatesGroup, State


class BuyStates(StatesGroup):
    EnterNumber = State()