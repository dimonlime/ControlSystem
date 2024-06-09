from aiogram.fsm.state import StatesGroup, State


class edit_order1(StatesGroup):
    select = State()
    edit_value = State()
    insert_quantity_s = State()
    insert_quantity_m = State()
    insert_quantity_l = State()
    edit_sending_method = State()


class edit_shipment(StatesGroup):
    select_shipment = State()
    edit_value = State()
    insert_quantity_s = State()
    insert_quantity_m = State()
    insert_quantity_l = State()
    edit_sending_method = State()


class edit_cheque(StatesGroup):
    select_cheque = State()


class edit_fish(StatesGroup):
    select_fish = State()
