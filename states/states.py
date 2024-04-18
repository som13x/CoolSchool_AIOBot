from aiogram.filters.state import State, StatesGroup


class UserInformation(StatesGroup):
    name = State()
    language_level = State()
    age = State()
    learn_target = State()
    telephone = State()
    time_priority = State()
