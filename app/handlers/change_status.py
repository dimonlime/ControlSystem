from datetime import datetime
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from app.id_config import recipients
from app.keyboards import async_keyboards as async_kb
from app.database import requests as rq

from app.states.create_cheque import create_cheque_state

router = Router()


"""Обработчик изменения статуса + чек-------------------------------------------------------------------------------"""


@router.message(F.text == 'Изменить статус заказа')
async def edit_order_status(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in recipients:
        await message.answer('Выберите поставку:', reply_markup=await async_kb.all_incomes_recipients())


@router.callback_query(F.data.startswith('income_rec'))
async def check_income_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    income_id = str(callback.data)[10:]
    income_id = int(income_id)
    await callback.message.answer('Выберите заказ:', reply_markup=await async_kb.inline_all_orders(income_id))


@router.callback_query(F.data.startswith('edit_status_'))
async def edit_order_status_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(create_cheque_state.select_order)
    order_id = str(callback.data)[12:]
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
                                        reply_markup=await async_kb.inline_order_status(), parse_mode="Markdown")


@router.callback_query(F.data.startswith('status_'), create_cheque_state.select_status)
async def edit_order_status_2(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    order_status = str(callback.data)[7:]
    data = await state.get_data()
    order = await rq.get_order(data['order_id'])
    if order_status == 'Готов' and await rq.get_cheque_by_orderid(data['order_id']) is None:
        await state.update_data(order_status=order_status)
        await state.set_state(create_cheque_state.insert_date_cheque)
        await callback.message.answer('Внимание, чтобы поменить статус, нужно создать чек')
        await callback.message.answer('Введите дату, указанную на чеке(пример 03-04-2024 15:34):')
    elif (order_status == 'Передан в логистику' and await rq.get_fish(data['order_id']) is None
          and await rq.get_cheque_by_orderid(data['order_id']) is not None):
        await state.update_data(order_status=order_status)
        await state.set_state(create_cheque_state.insert_fact_s)
        await callback.message.answer('Внимание, прежде чем менять статус, введите фактическое кол-во отправляемого '
                                      'товара')
        await callback.message.answer('Введите фактическое кол-во товара размера S:')
    elif (order_status == 'Передан в работу поставщику' and await rq.get_cheque_by_orderid(data['order_id']) is None
          and order.order_status == 'Заказ создан'):
        await state.update_data(order_status=order_status)
        await state.update_data(order_change_date=datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        data = await state.get_data()
        await rq.edit_order_status(data['order_id'], data['order_status'], data['order_change_date'])
        await callback.message.answer('Статус успешно обновлен')
    else:
        await callback.message.answer('Нельзя выполнить действие')


@router.message(create_cheque_state.insert_date_cheque)
async def insert_cheque_date(message: Message, state: FSMContext):
    try:
        message_date = str(message.text)
        cheque_date = datetime.strptime(message_date, "%d-%m-%Y %H:%M")
        if cheque_date <= datetime.now():
            await state.update_data(cheque_date=cheque_date.strftime("%d-%m-%Y %H:%M"))
            await state.set_state(create_cheque_state.insert_cheque_number)
            await message.answer('Введите номер чека:')
        else:
            await message.answer(f'Введите дату не позднее чем {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_cheque_number)
async def insert_cheque_number(message: Message, state: FSMContext):
    try:
        cheque_number = int(message.text)
        await state.update_data(cheque_number=cheque_number)
        await state.set_state(create_cheque_state.insert_vendor_article)
        await message.answer('Введите артикул поставщика:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_vendor_article)
async def insert_vendor_article(message: Message, state: FSMContext):
    try:
        vendor_article = int(message.text)
        await state.update_data(vendor_article=vendor_article)
        await state.set_state(create_cheque_state.insert_price_cheque)
        await message.answer('Введите цену:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_price_cheque)
async def insert_price_cheque(message: Message, state: FSMContext):
    try:
        price = str(message.text)
        await state.update_data(price=price)
        await state.set_state(create_cheque_state.insert_image_cheque)
        await message.answer('Отправьте фотографию чека:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_image_cheque)
async def insert_image_cheque(message: Message, state: FSMContext):
    try:
        await state.update_data(image=message.photo[-1].file_id)
        await state.update_data(order_change_date=datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        await state.update_data(date=datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        data = await state.get_data()
        order = await rq.get_order(data['order_id'])
        await rq.create_cheque_db(order.vendor_name, data['price'], data['image'], data['order_id'],
                                  data['cheque_date'], data['cheque_number'], data['vendor_article'], data['date'])
        await rq.edit_order_status(data['order_id'], data['order_status'], data['order_change_date'])
        await rq.set_order_cheque_image(data['order_id'], data['image'])
        order = await rq.get_order(data['order_id'])
        await message.answer(f'Чек создан успешно\n'
                             f'🔴Уникальный номер *{order.sack_number}*\n'
                             f'Данный номер нужно нанести на каждый мешок для поставки с артикулом {order.internal_article}'
                             , parse_mode="Markdown")
        await message.answer(f"Статус заказа изменен на {data['order_status']}")
        await state.clear()
    except TypeError:
        await message.answer('Ошибка, попробуйте еще раз')
