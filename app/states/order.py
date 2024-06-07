from aiogram.fsm.state import StatesGroup, State


class check_orders(StatesGroup):
    select_order = State()
    select_shipment = State()
    get_order = State()
    close_order = State()
    send_order_to_archive = State()


class archive_orders(StatesGroup):
    select_order = State()
    select_status = State()
    get_order = State()
