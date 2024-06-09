from datetime import datetime

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, InputMediaDocument
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.id_config import senders
from app.keyboards import async_keyboards as async_kb
from app.keyboards import static_keyboards as static_kb
from app.database.requests import order_request as order_rq
from app.database.requests import shipment_request as ship_rq
from app.database.requests import cheque_request as cheque_rq
from app.database.requests import fish_request as fish_rq
from app.utils.utils import enough_quantity_order, shipments_quantity_s, shipments_quantity_m, shipments_quantity_l, shipments_ready

from app.states.order import check_orders
from app.states.edit_data import edit_order1, edit_fish, edit_cheque, edit_shipment

router = Router()


@router.message(F.text == 'Редактировать данные')
async def create_order(message: Message, state: FSMContext):
    if message.from_user.id in senders:
        await state.clear()
        await message.answer('Меню редактирования:', reply_markup=static_kb.edit_data)


@router.message(F.text == 'Редактировать заказ')
async def create_order(message: Message, state: FSMContext):
    if message.from_user.id in senders:
        await state.set_state(edit_order1.select)
        await message.answer('Выберите заказ:', reply_markup=await async_kb.all_orders())


@router.message(F.text == 'Редактировать поставку')
async def create_order(message: Message, state: FSMContext):
    if message.from_user.id in senders:
        await state.set_state(edit_shipment.select_shipment)
        await message.answer('Выберите поставку:', reply_markup=await async_kb.all_shipments())


@router.message(F.text == 'Редактировать чек')
async def create_order(message: Message, state: FSMContext):
    if message.from_user.id in senders:
        await state.set_state(edit_cheque.select_cheque)
        await message.answer('Выберите чек:', reply_markup=await async_kb.all_cheques())


@router.message(F.text == 'Редактировать FIS`')
async def create_order(message: Message, state: FSMContext):
    if message.from_user.id in senders:
        await state.set_state(edit_fish.select_fish)
        await message.answer('Выберите FIS`:', reply_markup=await async_kb.all_fishes())


@router.callback_query(F.data.startswith('order_id_'), edit_order1.select)
async def edit_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    order_id = str(callback.data)[9:]
    order = await order_rq.get_order(order_id)
    await state.update_data(order=order, callback=callback, state=state)
    ship_s = await shipments_quantity_s(order_id)
    ship_m = await shipments_quantity_m(order_id)
    ship_l = await shipments_quantity_l(order_id)
    order_create_date = datetime.strptime(order.create_date, "%d-%m-%Y %H:%M:%S")
    caption = (f'------Данные заказа------\n'
               f'*Дата создания заказа:* _{str(order.create_date)}_\n'
               f'*Дата последнего изменения заказа:* _{str(order.change_date)}_\n'
               f'*Внутренний артикул товара:* _{str(order.internal_article)}_\n'
               f'*Внутренний артикул поставщика:* _{str(order.vendor_internal_article)}_\n'
               f'*Кол-во товара размера S:* _{str(order.quantity_s)}_\n'
               f'*Кол-во товара размера M:* _{str(order.quantity_m)}_\n'
               f'*Кол-во товара размера L:* _{str(order.quantity_l)}_\n'
               f'*Цвет:* _{str(order.color)}_\n'
               f'*Название магазина:* _{str(order.shop_name)}_\n'
               f'*Способ отправки:* _{str(order.sending_method)}_\n'
               f'*Статус заказа:* _{str(order.status)}_\n')
    if order.status != 'Заказ готов':
        caption += f'🔴 *Заказ не готов*\n'
    else:
        caption += f'🟢 *Заказ готов*\n'
    if not await enough_quantity_order(order_id):
        remain_s = order.quantity_s - ship_s
        remain_m = order.quantity_m - ship_m
        remain_l = order.quantity_l - ship_l
        await state.update_data(remain_s=remain_s, remain_m=remain_m, remain_l=remain_l)
        caption += f'🔴 *Ожидается* *S:* _{remain_s}_ *M:* _{remain_m}_ *L:* _{remain_l}_\n'
    else:
        caption += f'🟢 *Заказанное кол-во отправлено*\n'
    if not await shipments_ready(order_id):
        caption += f'🔴 *Не все поставки приняты на складе WB*\n'
    else:
        caption += f'🟢 *Все текущие поставки приняты на складе WB*\n'
    media_list = [InputMediaPhoto(media=order.order_image, caption=caption, parse_mode="Markdown")]
    await callback.message.answer_media_group(media=media_list)
    await state.set_state(edit_order1.edit_value)
    await callback.message.answer(f'Выберите поле для редактирования', reply_markup=static_kb.edit_order)


@router.callback_query(F.data == 'edit_quantity_s', edit_order1.edit_value)
async def edit_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(edit_order1.insert_quantity_s)
    await callback.message.answer('Введите новое кол-во товара S:')


@router.message(edit_order1.insert_quantity_s)
async def edit_order(message: Message, state: FSMContext):
    try:
        quantity_s = int(message.text)
        data = await state.get_data()
        await order_rq.insert_quantity_s(data['order'].id, quantity_s)
        await message.answer(f'Новое кол-во товара S: {quantity_s}')
        await state.set_state(edit_order1.edit_value)
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.callback_query(F.data == 'edit_quantity_m', edit_order1.edit_value)
async def edit_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(edit_order1.insert_quantity_m)
    await callback.message.answer('Введите новое кол-во товара M:')


@router.message(edit_order1.insert_quantity_m)
async def edit_order(message: Message, state: FSMContext):
    try:
        quantity_m = int(message.text)
        data = await state.get_data()
        await order_rq.insert_quantity_m(data['order'].id, quantity_m)
        await message.answer(f'Новое кол-во товара M: {quantity_m}')
        await state.set_state(edit_order1.edit_value)
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.callback_query(F.data == 'edit_quantity_l', edit_order1.edit_value)
async def edit_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(edit_order1.insert_quantity_l)
    await callback.message.answer('Введите новое кол-во товара L:')


@router.message(edit_order1.insert_quantity_l)
async def edit_order(message: Message, state: FSMContext):
    try:
        quantity_l = int(message.text)
        data = await state.get_data()
        await order_rq.insert_quantity_l(data['order'].id, quantity_l)
        await message.answer(f'Новое кол-во товара L: {quantity_l}')
        await state.set_state(edit_order1.edit_value)
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.callback_query(F.data == 'edit_sending_method', edit_order1.edit_value)
async def edit_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(edit_order1.edit_sending_method)
    await callback.message.answer('Выберите способ отправки', reply_markup=await async_kb.sending_method())


@router.callback_query(F.data.startswith('method_'), edit_order1.edit_sending_method)
async def edit_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        method = str(callback.data)[7:]
        data = await state.get_data()
        await order_rq.insert_sending_method(data['order'].id, method)
        await callback.message.answer(f'Способ отправки обновлен успешно')
        await state.set_state(edit_order1.edit_value)
    except ValueError:
        await callback.message.answer('Ошибка, попробуйте еще раз')


@router.callback_query(F.data.startswith('shipment_id_'), edit_shipment.select_shipment)
async def check_income_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    shipment_id = str(callback.data)[12:]
    shipment = await ship_rq.get_shipment(shipment_id)
    cheque = await cheque_rq.get_cheque(shipment_id)
    fish = await fish_rq.get_fish(shipment_id)
    order = await order_rq.get_order(shipment.order_id)
    await state.update_data(shipment_id=shipment_id, shipment=shipment, order=order, fish=fish, cheque=cheque)
    data = await state.get_data()
    media_list = []
    document_list = []
    await state.set_state(edit_shipment.edit_value)
    caption = (f'------Данные поставки------\n'
               f'*Дата отправки:* _{shipment.create_date}_\n'
               f'*Дата последнего изменения:* _{shipment.change_date}_\n'
               f'*Кол-во товара S:* _{shipment.quantity_s}_ M: _{shipment.quantity_m}_ L: _{shipment.quantity_l}_\n'
               f'*Статус:* _{shipment.status}_\n'
               f'*Способ отправки:* _{shipment.sending_method}_\n'
               f'------Данные чека------\n'
               f'*Дата чека:* _{str(cheque.date)}_\n'
               f'*Дата последнего изменения чека:* _{str(cheque.create_date)}_\n'
               f'*Номер чека:* _{str(cheque.cheque_number)}_\n'
               f'*Артикул поставщика:* _{str(cheque.vendor_internal_article)}_\n'
               f'*Цена:* _{str(cheque.price)}_\n'
               f'*Название магазина:* _{str(cheque.shop_name)}_\n'
               f'*Статус чека:* _{str(cheque.cheque_status)}_\n'
               f'------Данные fish------\n'
               f'*Номер fish:* _{str(fish.fish_number)}_\n'
               f'*Дата fish:* _{str(fish.fish_date)}_\n'
               f'*Вес:* _{str(fish.weight)} кг_\n'
               f'*Кол-во мешков:* _{str(fish.sack_count)}_\n'
               f'*Способ отправки:* _{str(fish.sending_method)}_\n')
    if shipment.status == 'Поставка отправлена':
        media_list.append(InputMediaPhoto(media=data['order'].order_image, caption=caption, parse_mode="Markdown"))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=fish.fish_image_id))
        if cheque.payment_image is not None:
            media_list.append(InputMediaPhoto(media=cheque.payment_image))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Выберите действие', reply_markup=static_kb.edit_shipment)
    elif shipment.status == 'Пришла в Москву':
        media_list.append(InputMediaPhoto(media=data['order'].order_image, caption=caption, parse_mode="Markdown"))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=fish.fish_image_id))
        if cheque.payment_image is not None:
            media_list.append(InputMediaPhoto(media=cheque.payment_image))
        media_list.append(InputMediaPhoto(media=shipment.image_1_id))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Выберите действие', reply_markup=static_kb.edit_shipment)
    elif shipment.status == 'Принята на складе ПД':
        media_list.append(InputMediaPhoto(media=data['order'].order_image, caption=caption, parse_mode="Markdown"))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=fish.fish_image_id))
        if cheque.payment_image is not None:
            media_list.append(InputMediaPhoto(media=cheque.payment_image))
        media_list.append(InputMediaPhoto(media=shipment.image_1_id))
        document_list.append(InputMediaDocument(media=shipment.document_1_id))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer_media_group(media=document_list)
        await callback.message.answer('Выберите действие', reply_markup=static_kb.edit_shipment)
    elif shipment.status == 'Отправлена на склад WB':
        media_list.append(InputMediaPhoto(media=data['order'].order_image, caption=caption, parse_mode="Markdown"))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=fish.fish_image_id))
        if cheque.payment_image is not None:
            media_list.append(InputMediaPhoto(media=cheque.payment_image))
        media_list.append(InputMediaPhoto(media=shipment.image_1_id))
        media_list.append(InputMediaPhoto(media=shipment.image_2_id))
        document_list.append(InputMediaDocument(media=shipment.document_1_id))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer_media_group(media=document_list)
        await callback.message.answer('Выберите действие', reply_markup=static_kb.edit_shipment)
    elif shipment.status == 'Принята на складе WB':
        media_list.append(InputMediaPhoto(media=data['order'].order_image, caption=caption, parse_mode="Markdown"))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=fish.fish_image_id))
        if cheque.payment_image is not None:
            media_list.append(InputMediaPhoto(media=cheque.payment_image))
        media_list.append(InputMediaPhoto(media=shipment.image_1_id))
        media_list.append(InputMediaPhoto(media=shipment.image_2_id))
        document_list.append(InputMediaDocument(media=shipment.document_1_id))
        document_list.append(InputMediaDocument(media=shipment.document_2_id))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer_media_group(media=document_list)
        await callback.message.answer('Выберите действие', reply_markup=static_kb.edit_shipment)


@router.callback_query(F.data == 'edit_quantity_s', edit_shipment.edit_value)
async def edit_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(edit_shipment.insert_quantity_s)
    await callback.message.answer('Введите новое кол-во товара S:')


@router.message(edit_shipment.insert_quantity_s)
async def edit_order(message: Message, state: FSMContext):
    try:
        quantity_s = int(message.text)
        data = await state.get_data()
        await ship_rq.insert_quantity_s(data['shipment'].id, quantity_s)
        await message.answer(f'Новое кол-во товара S: {quantity_s}')
        await state.set_state(edit_shipment.edit_value)
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.callback_query(F.data == 'edit_quantity_m', edit_shipment.edit_value)
async def edit_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(edit_shipment.insert_quantity_m)
    await callback.message.answer('Введите новое кол-во товара M:')


@router.message(edit_shipment.insert_quantity_m)
async def edit_order(message: Message, state: FSMContext):
    try:
        quantity_m = int(message.text)
        data = await state.get_data()
        await ship_rq.insert_quantity_m(data['shipment'].id, quantity_m)
        await message.answer(f'Новое кол-во товара M: {quantity_m}')
        await state.set_state(edit_shipment.edit_value)
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.callback_query(F.data == 'edit_quantity_l', edit_shipment.edit_value)
async def edit_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(edit_shipment.insert_quantity_l)
    await callback.message.answer('Введите новое кол-во товара L:')


@router.message(edit_shipment.insert_quantity_l)
async def edit_order(message: Message, state: FSMContext):
    try:
        quantity_l = int(message.text)
        data = await state.get_data()
        await ship_rq.insert_quantity_l(data['shipment'].id, quantity_l)
        await message.answer(f'Новое кол-во товара L: {quantity_l}')
        await state.set_state(edit_shipment.edit_value)
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')