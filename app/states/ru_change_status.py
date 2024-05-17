from aiogram.fsm.state import StatesGroup, State


class edit_ru_order_status(StatesGroup):
    select_order = State()
    select_status = State()

    insert_excel_1 = State()
    insert_screen_1 = State()
    insert_excel_2 = State()
    insert_screen_2 = State()



