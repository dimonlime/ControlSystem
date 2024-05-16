from aiogram.fsm.state import StatesGroup, State


class change_cheque_status(StatesGroup):
    select_cheque = State()
    attach_pay_screen = State()