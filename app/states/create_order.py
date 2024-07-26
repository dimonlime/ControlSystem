from aiogram.fsm.state import StatesGroup, State


class create_order_state(StatesGroup):
    insert_internal_article = State()
    insert_date_order = State()
    insert_xs_order = State()
    insert_s_order = State()
    insert_m_order = State()
    insert_l_order = State()
    insert_vendor_order = State()
    insert_sending_method = State()
    insert_order_image_id = State()
    insert_delivery_id = State()
    insert_delivery_date = State()
    insert_color = State()
    insert_vendor_internal_article = State()
    create_order = State()