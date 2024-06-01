from aiogram.fsm.state import StatesGroup, State


class view_cheque_state(StatesGroup):
    select_cheque = State()
    view_cheque = State()
    pay_cheque = State()
    insert_payment_image = State()
