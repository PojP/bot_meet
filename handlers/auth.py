from aiogram.dispatcher.filters.state import State, StatesGroup
class IsAuthorized(StatesGroup):
    is_auth=State()