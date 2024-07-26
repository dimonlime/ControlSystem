from aiogram.fsm.state import StatesGroup, State


class create_shipment_state(StatesGroup):
    select_order = State()
    insert_quantity_xs = State()
    insert_quantity_s = State()
    insert_quantity_m = State()
    insert_quantity_l = State()
    create_shipment = State()


class create_cheque_state(StatesGroup):
    insert_date = State()
    insert_cheque_number = State()
    insert_vendor_internal_article = State()
    insert_price = State()
    insert_cheque_image = State()


class create_fish_state(StatesGroup):
    insert_fish_number = State()
    insert_date = State()
    insert_weight = State()
    insert_sack_count = State()
    insert_fish_image = State()


class change_shipment_status_state(StatesGroup):
    select_shipment = State()
    select_status = State()
    insert_image_1 = State()
    insert_image_2 = State()
    insert_document_1 = State()
    insert_document_2 = State()
