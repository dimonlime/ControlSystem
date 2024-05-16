from datetime import datetime
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.id_config import senders, ru_order_status
from app.keyboards import async_keyboards as async_kb
from app.database import requests as rq

router = Router()


class create_cheque_state(StatesGroup):
    select_order = State()
    select_status = State()
    insert_date_cheque = State()
    insert_price_cheque = State()
    insert_image_cheque = State()
    insert_cheque_number = State()
    insert_vendor_article = State()

    insert_fact_s = State()


"""Обработчик изменения статуса + чек-------------------------------------------------------------------------------"""


@router.message(F.text == 'Изменить статус заказов')
async def edit_order_status(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in senders:
        await message.answer('Выберите поставку:', reply_markup=await async_kb.all_incomes_senders())


@router.callback_query(F.data.startswith('income_send_'))
async def check_income_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    income_id = str(callback.data)[12:]
    income_id = int(income_id)
    await callback.message.answer('Выберите заказ:', reply_markup=await async_kb.inline_all_orders_ru(income_id))


@router.callback_query(F.data.startswith('ru_edit_status_'))
async def edit_order_status_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(create_cheque_state.select_order)
    order_id = str(callback.data)[15:]
    await state.update_data(order_id=order_id)
    order = await rq.get_order(order_id)
    await state.set_state(create_cheque_state.select_status)
    await callback.message.answer_photo(caption=f'*------Данные заказа------*\n'
                                                f'*Дата создания заказа:* {str(order.date)}\n'
                                                f'*Дата последнего изменения заказа:* {str(order.change_date)}\n'
                                                f'*Внутренний артикул товара:* {str(order.internal_article)}\n'
                                                f'*Внутренний артикул поставщика:* {str(order.vendor_internal_article)}\n'
                                                f'*Кол-во товара размера S:* {str(order.S)}\n'
                                                f'*Кол-во товара размера M:* {str(order.M)}\n'
                                                f'*Кол-во товара размера L:* {str(order.L)}\n'
                                                f'*Цвет:* {str(order.color)}\n'
                                                f'*Название магазина:* {str(order.vendor_name)}\n'
                                                f'*Способ отправки:* {str(order.sending_method)}\n'
                                                f'*Статус заказа:* {str(order.order_status)}\n',
                                        photo=order.order_image_id,
                                        reply_markup=await async_kb.inline_ru_order_status(), parse_mode="Markdown")


@router.callback_query(F.data.startswith('ru_status_'), create_cheque_state.select_status)
async def edit_order_status_2(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    order_status = str(callback.data)[10:]
    data = await state.get_data()
    order = await rq.get_order(data['order_id'])
    change_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    await rq.edit_order_status(order.id, order_status, change_date)
    await callback.message.answer('Статус успешно обновлен')
