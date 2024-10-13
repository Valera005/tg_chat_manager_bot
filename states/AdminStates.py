from aiogram.dispatcher.filters.state import StatesGroup, State


class AddLink(StatesGroup):
    S1 = State()


class AddChannel(StatesGroup):
    S1 = State()
    S2 = State()