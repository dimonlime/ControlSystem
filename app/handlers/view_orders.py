from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.id_config import senders
from app.keyboards import async_keyboards as async_kb
from app.keyboards import static_keyboards as static_kb
from app.database import requests as rq

router = Router()


class check_orders(StatesGroup):
    select_order = State()
    select_status = State()
    get_order = State()


"""Просмотр заказов-------------------------------------------------------------------------------------------------"""


@router.message(F.text == 'Посмотреть заказы')
async def check_all_orders(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in senders:
        await message.answer('Выберите поставку:', reply_markup=await async_kb.all_incomes())


@router.callback_query(F.data.startswith('income_all_'))
async def check_income_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(check_orders.select_status)
    income_id = str(callback.data)[11:]
    income_id = int(income_id)
    await state.update_data(income_id=income_id)
    await callback.message.answer('Выберите статус заказа:', reply_markup=await async_kb.inline_all_orders_status(income_id))


@router.callback_query(F.data.startswith('order_status_'), check_orders.select_status)
async def check_income_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    order_status = str(callback.data)[13:]
    await state.update_data(order_status=order_status)
    data = await state.get_data()
    await callback.message.answer(f'Выберите заказ({order_status}):', reply_markup=await async_kb.inline_all_orders_by_status(data['income_id'], data['order_status']))


@router.callback_query(F.data.startswith('orders_all'), check_orders.select_status)
async def check_income_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    await callback.message.answer('Выберите заказ:', reply_markup=await async_kb.inline_all_orders_send(data['income_id']))


@router.callback_query(F.data.startswith('get_info_'))
async def get_all_orders(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(check_orders.select_order)
    order_id = str(callback.data)[9:]
    order = await rq.get_order(order_id)
    cheque = await rq.get_cheque_by_orderid(order_id)
    fish = await rq.get_fish_obj(order_id)
    await state.update_data(order_id=order_id)
    media_list = []
    if order.cheque_image_id is None and order.fish is None:
        media_list.append(InputMediaPhoto(media=order.order_image_id))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Выберите действие:', reply_markup=static_kb.view_info)
    elif cheque.cheque_image_id is not None and order.fish is None and cheque.payment_image is None:
        await state.update_data(cheque_id=cheque.id)
        media_list.append(InputMediaPhoto(media=order.order_image_id))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Выберите действие:', reply_markup=static_kb.view_info)
    elif cheque.payment_image is not None and order.fish is None and cheque.cheque_image_id is not None:
        await state.update_data(cheque_id=cheque.id)
        media_list.append(InputMediaPhoto(media=order.order_image_id))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=cheque.payment_image))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Выберите действие:', reply_markup=static_kb.view_info)
    elif order.cheque_image_id is not None and cheque.payment_image is not None and order.fish is not None:
        await state.update_data(cheque_id=cheque.id)
        media_list.append(InputMediaPhoto(media=order.order_image_id))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=cheque.payment_image))
        media_list.append(InputMediaPhoto(media=fish.fish_image_id))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Выберите действие:', reply_markup=static_kb.view_info)
    elif order.cheque_image_id is not None and cheque.payment_image is None and order.fish is not None:
        await state.update_data(cheque_id=cheque.id)
        media_list.append(InputMediaPhoto(media=order.order_image_id))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=fish.fish_image_id))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Выберите действие:', reply_markup=static_kb.view_info)


@router.callback_query(F.data == 'order_info', check_orders.select_order)
async def order_info(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    order = await rq.get_order(data['order_id'])
    try:
        await callback.message.answer(
            f'*------Данные заказа------*\n'
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
            f'*Статус заказа:* {str(order.order_status)}\n', parse_mode="Markdown")
    except AttributeError:
        await callback.message.answer('Нет данных')


@router.callback_query(F.data == 'cheque_info', check_orders.select_order)
async def cheque_info(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    cheque = await rq.get_cheque_by_orderid(data['order_id'])
    try:
        await callback.message.answer(
            f'*------Данные чека------*\n'
            f'*Дата чека:* {str(cheque.cheque_date)}\n'
            f'*Дата последнего изменения чека:* {str(cheque.date)}\n'
            f'*Номер чека:* {str(cheque.cheque_number)}\n'
            f'*Артикул поставщика:* {str(cheque.vendor_article)}\n'
            f'*Цена:* {str(cheque.price)}\n'
            f'*Название магазина:* {str(cheque.vendor_name)}\n'
            f'*Статус чека:* {str(cheque.cheque_status)}\n', parse_mode="Markdown")
    except AttributeError:
        await callback.message.answer('Нет данных')


@router.callback_query(F.data == 'fish_info', check_orders.select_order)
async def fish_info(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    fish = await rq.get_fish_obj(data['order_id'])
    try:
        await callback.message.answer(
            f'*------Данные fish------*\n'
            f'*Номер fish:* {str(fish.fish)}\n'
            f'*Дата fish:* {str(fish.date)}\n'
            f'*Вес:* {str(fish.weight)} кг\n'
            f'*Кол-во мешков:* {str(fish.sack_count)}\n'
            f'*Способ отправки:* {str(fish.sending_method)}\n', parse_mode="Markdown")
    except AttributeError:
        await callback.message.answer('Нет данных')


@router.callback_query(F.data == 'fact_info', check_orders.select_order)
async def fact_info(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    order = await rq.get_order(data['order_id'])
    if order.fact_S is not None:
        await callback.message.answer(
            f'*------Фактические данные------*\n'
            f'*Фактическое кол-во товара размера S:* {str(order.fact_S)}, *расхождение с заказом:* {order.fact_S - order.S}\n'
            f'*Фактическое кол-во товара размера M:* {str(order.fact_M)}, *расхождение с заказом:* {order.fact_M - order.M}\n'
            f'*Фактическое кол-во товара размера L:* {str(order.fact_L)}, *расхождение с заказом:* {order.fact_L - order.L}\n',
            parse_mode="Markdown")
    else:
        await callback.message.answer('Нет данных')


@router.callback_query(F.data == 'all_info', check_orders.select_order)
async def all_info(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    cheque = await rq.get_cheque_by_orderid(data['order_id'])
    order = await rq.get_order(data['order_id'])
    fish = await rq.get_fish_obj(data['order_id'])
    try:
        order_string = (
            f'------Данные заказа------\n'
            f'Дата создания заказа: {str(order.date)}\n'
            f'Дата последнего изменения заказа: {str(order.change_date)}\n'
            f'Внутренний артикул товара: {str(order.internal_article)}\n'
            f'Внутренний артикул поставщика: {str(order.vendor_internal_article)}\n'
            f'Кол-во товара размера S: {str(order.S)}\n'
            f'Кол-во товара размера M: {str(order.M)}\n'
            f'Кол-во товара размера L: {str(order.L)}\n'
            f'Цвет: {str(order.color)}\n'
            f'Название магазина: {str(order.vendor_name)}\n'
            f'Способ отправки: {str(order.sending_method)}\n'
            f'Номер для мешков: {str(order.sack_number)}\n'
            f'Статус заказа: {str(order.order_status)}\n')
    except AttributeError:
        order_string = ''
    try:
        cheque_string = (
            f'------Данные чека------\n'
            f'Дата чека: {str(cheque.cheque_date)}\n'
            f'Дата последнего изменения чека: {str(cheque.date)}\n'
            f'Номер чека: {str(cheque.cheque_number)}\n'
            f'Артикул поставщика: {str(cheque.vendor_article)}\n'
            f'Цена: {str(cheque.price)}\n'
            f'Название магазина: {str(cheque.vendor_name)}\n'
            f'Статус чека: {str(cheque.cheque_status)}\n')
    except AttributeError:
        cheque_string = ''
    try:
        fish_string = (
            f'------Данные fish------\n'
            f'Номер fish: {str(fish.fish)}\n'
            f'Дата fish: {str(fish.date)}\n'
            f'Вес: {str(fish.weight)} кг\n'
            f'Кол-во мешков: {str(fish.sack_count)}\n'
            f'Способ отправки: {str(fish.sending_method)}\n')
    except AttributeError:
        fish_string = ''
    if order.fact_S is not None:
        fact_string = (
            f'------Фактические данные------\n'
            f'Фактическое кол-во товара размера S: {str(order.fact_S)}, расхождение с заказом: {order.fact_S - order.S}\n'
            f'Фактическое кол-во товара размера M: {str(order.fact_M)}, расхождение с заказом: {order.fact_M - order.M}\n'
            f'Фактическое кол-во товара размера L: {str(order.fact_L)}, расхождение с заказом: {order.fact_L - order.L}\n')
    else:
        fact_string = ''
    info_string = order_string + cheque_string + fish_string + fact_string
    await callback.message.answer(info_string)
