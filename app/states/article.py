from aiogram.fsm.state import StatesGroup, State


class check_article(StatesGroup):
    select_article = State()
    view_article = State()