from aiogram.fsm.state import StatesGroup, State


class create_article(StatesGroup):
    insert_article = State()
    insert_image = State()


class view_article(StatesGroup):
    select_article = State()
    replace_image = State()
    insert_image = State()


class remove_article(StatesGroup):
    select_article = State()
