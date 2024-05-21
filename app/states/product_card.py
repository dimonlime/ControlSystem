from aiogram.fsm.state import StatesGroup, State


class create_product_card(StatesGroup):
    insert_article = State()
    insert_image = State()
    insert_color = State()
    insert_shop_name = State()
    insert_vendor_internal_article = State()


class view_product_card(StatesGroup):
    select_article = State()
    replace_image = State()
    insert_image = State()


class remove_product_card(StatesGroup):
    select_article = State()
