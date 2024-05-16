from aiogram.fsm.state import StatesGroup, State


class check_orders(StatesGroup):
    select_order = State()
    select_status = State()
    get_order = State()
