from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from app.id_config import recipients
from app.keyboards import async_keyboards as async_kb
from app.keyboards import static_keyboards as static_kb
from app.database import requests as rq

from app.states.change_cheque_status import change_cheque_status

router = Router()


"""Проверка чеков---------------------------------------------------------------------------------------------------"""


@router.message(F.text == 'Проверить чеки')
async def check_cheques(message: Message, state: FSMContext):
    if message.from_user.id in recipients:
        await message.answer('Выберите категорию чека:', reply_markup=static_kb.cheques_category_2)


@router.callback_query(F.data == 'paid_cheques')
async def get_paid_cheques(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Список оплаченных чеков', reply_markup=await async_kb.inline_paid_cheques())


@router.callback_query(F.data == 'unpaid_cheques')
async def get_unpaid_cheques(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Список не оплаченных чеков', reply_markup=await async_kb.inline_unpaid_cheques())


@router.callback_query(F.data.startswith('view_cheque_'))
async def view_cheque(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(change_cheque_status.select_cheque)
    cheque_id = str(callback.data)[12:]
    cheque = await rq.get_cheque(cheque_id)
    order = await rq.get_order(cheque.order_id)
    fish = await rq.get_fish_obj(order.id)
    await state.update_data(order_id=cheque.order_id, cheque_id=cheque.id)
    media_list = []
    if cheque.payment_image is None and order.fish is None:
        media_list.append(InputMediaPhoto(media=order.order_image_id))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Вывести информацию:', reply_markup=static_kb.view_info)
    elif order.fish is not None and cheque.payment_image is not None:
        media_list.append(InputMediaPhoto(media=order.order_image_id))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=cheque.payment_image))
        media_list.append(InputMediaPhoto(media=fish.fish_image_id))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Вывести информацию:', reply_markup=static_kb.view_info)
    elif order.fish is not None and cheque.payment_image is None:
        media_list.append(InputMediaPhoto(media=order.order_image_id))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=fish.fish_image_id))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Вывести информацию:', reply_markup=static_kb.view_info)
    elif cheque.payment_image is not None:
        media_list.append(InputMediaPhoto(media=order.order_image_id))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=cheque.payment_image))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Вывести информацию:', reply_markup=static_kb.view_info)


@router.callback_query(F.data == 'order_info', change_cheque_status.select_cheque)
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


@router.callback_query(F.data == 'cheque_info', change_cheque_status.select_cheque)
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


@router.callback_query(F.data == 'fish_info', change_cheque_status.select_cheque)
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


@router.callback_query(F.data == 'fact_info', change_cheque_status.select_cheque)
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


@router.callback_query(F.data == 'all_info', change_cheque_status.select_cheque)
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
