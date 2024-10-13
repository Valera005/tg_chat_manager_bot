from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Update


class ManyExceptionsFilter(BoundFilter):
    def __init__(self, exceptions):
        self.exceptions = exceptions

    async def check(self, update : Update, exception) -> bool:
        return type(exception) in self.exceptions