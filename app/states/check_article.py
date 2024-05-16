from aiogram.fsm.state import StatesGroup, State


class check_articles(StatesGroup):
    select_article = State()
