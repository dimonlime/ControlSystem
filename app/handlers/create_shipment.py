from datetime import datetime
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from app.id_config import recipients
from app.keyboards import async_keyboards as async_kb
from app.keyboards import static_keyboards as static_kb
from app.database.requests import order_request as order_rq
from app.database.requests import cheque_request as cheque_rq
from app.database.requests import fish_request as fish_rq
from app.database.requests import shipment_request as ship_rq
from app.database.requests import product_card_request as card_rq
from app.utils.utils import product_card_exists, enough_quantity_order, shipments_quantity_s, shipments_quantity_m, \
    shipments_quantity_l

from app.states.shipment import create_shipment_state, create_cheque_state, create_fish_state

router = Router()

"""Создание заказа--------------------------------------------------------------------------------------------------"""


@router.message(F.text == 'Создать поставку')
async def create_order(message: Message, state: FSMContext):
    if message.from_user.id in recipients:
        await state.set_state(create_shipment_state.select_order)
        await message.answer('Выберите заказ:', reply_markup=await async_kb.recipient_orders())


@router.callback_query(F.data.startswith('order_id_'), create_shipment_state.select_order)
async def check_income_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    order_id = str(callback.data)[9:]
    await state.update_data(order_id=order_id)
    order = await order_rq.get_order(order_id)
    await state.update_data(order=order)
    ship_s = await shipments_quantity_s(order_id)
    ship_m = await shipments_quantity_m(order_id)
    ship_l = await shipments_quantity_l(order_id)
    remain_s = order.quantity_s - ship_s
    remain_m = order.quantity_m - ship_m
    remain_l = order.quantity_l - ship_l
    order_create_date = datetime.strptime(order.create_date, "%d-%m-%Y %H:%M:%S")
    media_list = [InputMediaPhoto(media=order.order_image,
                                  caption=f'*Артикул:* _{order.internal_article}_\n'
                                          f'*Дата создания заказа:* _{datetime.strftime(order_create_date, "%d-%m-%Y %H:%M")}_\n'
                                          f'*S:* _{order.quantity_s} _*M:* _{order.quantity_m}_ *L:* _{order.quantity_l}_\n'
                                          f'*Цвет:* _{order.color}_\n'
                                          f'*Название магазина:* _{order.shop_name}_\n'
                                          f'*Способ отправки:* _{order.sending_method}_\n'
                                          f'------------------------------\n'
                                          f'*Вы отправили:* *S:* _{ship_s}_ *M:* _{ship_m}_ *L:* _{ship_l}_\n'
                                          f'*Осталось отправить:* *S:* _{remain_s}_ *M:* _{remain_m}_ *L:* _{remain_l}_\n',
                                  parse_mode="Markdown")]
    await callback.message.answer_media_group(media=media_list)
    await callback.message.answer(f'Выберите действие', reply_markup=static_kb.recipient_order)


@router.callback_query(F.data == 'create_shipment')
async def check_income_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(create_cheque_state.insert_date)
    await callback.message.answer('Для создания поставки нужно ввести данные чека!')
    await callback.message.answer(f'Введите дату, указанную на чеке\n'
                                  f'Пример: {datetime.now().strftime("%d-%m-%Y %H:%M")}')


@router.message(create_shipment_state.insert_quantity_s)
async def insert_fish_image(message: Message, state: FSMContext):
    try:
        quantity_s = int(message.text)
        await state.update_data(shipment_quantity_s=quantity_s)
        await message.answer('Введите кол-во отправляемого товара размера M:')
        await state.set_state(create_shipment_state.insert_quantity_m)
    except TypeError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_shipment_state.insert_quantity_m)
async def insert_fish_image(message: Message, state: FSMContext):
    try:
        quantity_m = int(message.text)
        await state.update_data(shipment_quantity_m=quantity_m)
        await message.answer('Введите кол-во отправляемого товара размера L:')
        await state.set_state(create_shipment_state.insert_quantity_l)
    except TypeError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_shipment_state.insert_quantity_l)
async def insert_fish_image(message: Message, state: FSMContext):
    try:
        quantity_l = int(message.text)
        await state.update_data(shipment_quantity_l=quantity_l)
        await state.set_state(create_shipment_state.create_shipment)
        await create_shipment(message, state)
    except TypeError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_shipment_state.create_shipment)
async def create_shipment(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        shipment_create_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        await state.update_data(shipment_create_date=shipment_create_date)
        await cheque_rq.create_cheque_db(data['order'].id, data['cheque_create_date'], data['cheque_date'],
                                         data['order'].shop_name, data['cheque_number'], data['cheque_vendor_article'],
                                         data['cheque_price'], data['cheque_image'])
        await message.answer('Чек создан успешно!')
        await fish_rq.create_fish_db(data['order'].id, data['fish_number'], data['fish_date'], data['fish_weight'],
                                     data['fish_sack_count'], data['order'].sending_method, data['fish_image'])
        await message.answer('FIS` создан успешно!')
        cheque = await cheque_rq.get_last_cheque(data['order'].id)
        fish = await fish_rq.get_last_fish(data['order'].id)
        await state.update_data(cheque=cheque.first())
        await state.update_data(fish=fish.first())
        data = await state.get_data()
        await ship_rq.create_shipment_db(data['order_id'], data['shipment_create_date'], data['shipment_quantity_s'],
                                         data['shipment_quantity_m'], data['shipment_quantity_l'], data['order'].sending_method,
                                         data['fish'].id, data['cheque'].id)
        shipment = await ship_rq.get_last_ship(data['order'].id)
        await cheque_rq.insert_shipment_id(data['cheque'].id, shipment.first().id)
        shipment = await ship_rq.get_last_ship(data['order'].id)
        await fish_rq.insert_shipment_id(data['fish'].id, shipment.first().id)
        await message.answer('Поставка создана успешно!')
        await state.clear()
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')
