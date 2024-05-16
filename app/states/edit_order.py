from aiogram.fsm.state import StatesGroup, State


class edit_orders(StatesGroup):
    select_value = State()
    edit_product_article = State()
    edit_vendor_article = State()
    edit_s_quantity = State()
    edit_m_quantity = State()
    edit_l_quantity = State()
    edit_color = State()
    edit_name = State()
    edit_sending_method = State()