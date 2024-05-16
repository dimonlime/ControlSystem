from aiogram.fsm.state import StatesGroup, State


class create_cheque_state(StatesGroup):
    select_order = State()
    select_status = State()
    insert_date_cheque = State()
    insert_price_cheque = State()
    insert_image_cheque = State()
    insert_cheque_number = State()
    insert_vendor_article = State()

    insert_fact_s = State()
    insert_fact_m = State()
    insert_fact_l = State()

    insert_fish = State()
    insert_fish_date = State()
    insert_fish_weight = State()
    insert_sack_count = State()
    insert_fish_image_id = State()