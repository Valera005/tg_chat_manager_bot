from aiogram import Dispatcher

from filters.my_filters import ManyExceptionsFilter


def setup(dp: Dispatcher):
    dp.filters_factory.bind(ManyExceptionsFilter)
