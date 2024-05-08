from datetime import datetime, timedelta
import json

import aiogram.utils.magic_filter
from aiogram import types, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import CallbackQuery, Message, InputMedia, InputMediaPhoto
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.id_config import senders, recipients
from app import keyboards as kb
from app.database import requests as rq
import json

router = Router()


class create_order_state(StatesGroup):
    insert_internal_article = State()
    insert_date_order = State()
    insert_s_order = State()
    insert_m_order = State()
    insert_l_order = State()
    insert_vendor_order = State()
    insert_sending_method = State()
    insert_order_image_id = State()
    insert_delivery_id = State()
    insert_color = State()
    insert_vendor_internal_article = State()


class create_cheque_state(StatesGroup):
    select_order = State()
    select_status = State()
    attach_cheque_image = State()
    insert_date_cheque = State()
    insert_vendor_cheque = State()
    insert_price_cheque = State()
    insert_image_cheque = State()
    insert_cheque_number = State()
    insert_vendor_article = State()

    insert_fact_s = State()
    insert_fact_m = State()
    insert_fact_l = State()

    insert_fish = State()
    insert_fish_date = State()
    insert_fish_weight = State()
    insert_sack_count = State()
    insert_fish_image_id = State()


class change_cheque_status(StatesGroup):
    select_cheque = State()
    attach_pay_screen = State()


class check_orders(StatesGroup):
    select_order = State()


class edit_orders(StatesGroup):
    select_value = State()
    edit_product_article = State()
    edit_vendor_article = State()
    edit_s_quantity = State()
    edit_m_quantity = State()
    edit_l_quantity = State()
    edit_color = State()
    edit_name = State()
    edit_sending_method = State()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    if message.from_user.id in senders:
        await state.clear()
        await message.answer(
            f'{message.from_user.first_name} добро пожаловать, вы авторизованы как отправляющая сторона',
            reply_markup=kb.sender_keyboard)
    elif message.from_user.id in recipients:
        await state.clear()
        await message.answer(
            f'{message.from_user.first_name} добро пожаловать, вы авторизованы как принимающая сторона',
            reply_markup=kb.recipient_keyboard)


"""Обработчик изменения статуса + чек-------------------------------------------------------------------------------"""


@router.message(F.text == 'Изменить статус заказа')
async def edit_order_status(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in recipients:
        await message.answer('Выберите поставку:', reply_markup=await kb.all_incomes_recipients())


@router.callback_query(F.data.startswith('income_rec'))
async def check_income_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    income_id = str(callback.data)[10:]
    income_id = int(income_id)
    await callback.message.answer('Выберите заказ:', reply_markup=await kb.inline_all_orders(income_id))


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
                                        reply_markup=await kb.inline_order_status(), parse_mode="Markdown")


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


"""Заполнение фактических данных + переход на заполнение fish-------------------------------------------------------"""


@router.message(create_cheque_state.insert_fact_s)
async def insert_fact_s(message: Message, state: FSMContext):
    try:
        fact_s = int(message.text)
        await state.update_data(fact_s=fact_s)
        await state.set_state(create_cheque_state.insert_fact_m)
        await message.answer('Введите фактическое кол-во товара размера M')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_fact_m)
async def insert_fact_m(message: Message, state: FSMContext):
    try:
        fact_m = int(message.text)
        await state.update_data(fact_m=fact_m)
        await state.set_state(create_cheque_state.insert_fact_l)
        await message.answer('Введите фактическое кол-во товара размера L')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_fact_l)
async def insert_fact_l(message: Message, state: FSMContext):
    try:
        fact_l = int(message.text)
        await state.update_data(fact_l=fact_l)
        data = await state.get_data()
        await rq.insert_fact(data['order_id'], data['fact_s'], data['fact_m'], data['fact_l'], )
        await message.answer('Фактические данные введены успешно')
        await state.set_state(create_cheque_state.insert_fish)
        await message.answer('Внимание, чтобы поменить статус, нужно приложить FISH')
        await message.answer('Введите номер FISH для данного заказа:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


"""Создание fish----------------------------------------------------------------------------------------------------"""


@router.message(create_cheque_state.insert_fish)
async def insert_fish(message: Message, state: FSMContext):
    try:
        fish = int(message.text)
        await state.update_data(fish=fish)
        await state.set_state(create_cheque_state.insert_fish_date)
        await message.answer('Введите дату(пример 03-03-2023 23:23:23')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_fish_date)
async def insert_fish_date(message: Message, state: FSMContext):
    try:
        message_date = str(message.text)
        fish_date = datetime.strptime(message_date, "%d-%m-%Y %H:%M:%S")
        if fish_date <= datetime.now():
            await state.update_data(fish_date=fish_date.strftime("%d-%m-%Y %H:%M:%S"))
            await state.set_state(create_cheque_state.insert_fish_weight)
            await message.answer('Введите вес в кг:')
        else:
            await message.answer(f'Введите дату не позднее чем {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_fish_weight)
async def insert_fish_weight(message: Message, state: FSMContext):
    try:
        weight = int(message.text)
        await state.update_data(weight=weight)
        await state.set_state(create_cheque_state.insert_sack_count)
        await message.answer('Введите кол-во мешков:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_sack_count)
async def insert_fish_sack_count(message: Message, state: FSMContext):
    try:
        sack_count = int(message.text)
        await state.update_data(sack_count=sack_count)
        await state.set_state(create_cheque_state.insert_fish_image_id)
        await message.answer('Прикрепите фотографию FISH:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_fish_image_id)
async def insert_fish_image(message: Message, state: FSMContext):
    try:
        await state.update_data(fish_image=message.photo[-1].file_id)
        await state.update_data(order_change_date=datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        data = await state.get_data()
        order = await rq.get_order(data['order_id'])
        await rq.create_fish(data['fish'], data['fish_date'], data['weight'], data['sack_count'], order.sending_method,
                             data['fish_image'], data['order_id'])
        await rq.set_order_fish(data['order_id'], data['fish'])
        await rq.edit_order_status(data['order_id'], data['order_status'], data['order_change_date'])
        await message.answer('FISH прикрплен')
        await message.answer(f'Статус заказа изменен на {data["order_status"]}')
        await state.clear()
    except TypeError:
        await message.answer('Ошибка, попробуйте еще раз')


"""Проверка чеков---------------------------------------------------------------------------------------------------"""


@router.message(F.text == 'Проверить чеки')
async def check_cheques(message: Message, state: FSMContext):
    if message.from_user.id in recipients:
        await message.answer('Выберите категорию чека:', reply_markup=kb.cheques_category_2)


@router.callback_query(F.data == 'paid_cheques')
async def get_paid_cheques(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Список оплаченных чеков', reply_markup=await kb.inline_paid_cheques())


@router.callback_query(F.data == 'unpaid_cheques')
async def get_unpaid_cheques(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Список не оплаченных чеков', reply_markup=await kb.inline_unpaid_cheques())


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
        await callback.message.answer('Вывести информацию:', reply_markup=kb.view_info)
    elif order.fish is not None and cheque.payment_image is not None:
        media_list.append(InputMediaPhoto(media=order.order_image_id))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=cheque.payment_image))
        media_list.append(InputMediaPhoto(media=fish.fish_image_id))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Вывести информацию:', reply_markup=kb.view_info)
    elif order.fish is not None and cheque.payment_image is None:
        media_list.append(InputMediaPhoto(media=order.order_image_id))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=fish.fish_image_id))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Вывести информацию:', reply_markup=kb.view_info)
    elif cheque.payment_image is not None:
        media_list.append(InputMediaPhoto(media=order.order_image_id))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=cheque.payment_image))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Вывести информацию:', reply_markup=kb.view_info)


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


"""Создание заказа--------------------------------------------------------------------------------------------------"""


@router.message(F.text == 'Создать заказ')
async def create_order(message: Message, state: FSMContext):
    if message.from_user.id in senders:
        await state.set_state(create_order_state.insert_delivery_id)
        await message.answer('Введите ID поставки к которой относится заказ:')


@router.message(create_order_state.insert_delivery_id)
async def insert_delivery_id(message: Message, state: FSMContext):
    try:
        delivery_id = int(message.text)
        if delivery_id > 0:
            await state.update_data(delivery_id=delivery_id)
            await state.set_state(create_order_state.insert_internal_article)
            await message.answer('Введите внутренний артикул товара:')
        else:
            await message.answer('ID поставки не может быть меньше нуля...')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_order_state.insert_internal_article)
async def insert_internal_article(message: Message, state: FSMContext):
    try:
        internal_article = str(message.text)
        await state.update_data(internal_article=internal_article)
        await state.set_state(create_order_state.insert_vendor_internal_article)
        await message.answer('Введите внутренний артикул поставщика:', reply_markup=kb.vendor_internal_article)
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_order_state.insert_vendor_internal_article)
async def insert_vendor_internal_article(message: Message, state: FSMContext):
    try:
        vendor_internal_article = str(message.text)
        await state.update_data(vendor_internal_article=vendor_internal_article)
        await state.set_state(create_order_state.insert_s_order)
        await message.answer('Введите кол-во товара размера S:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.callback_query(F.data == 'skip', create_order_state.insert_vendor_internal_article)
async def skip_vendor_internal_article(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    vendor_internal_article = 'Не заполнено'
    await state.update_data(vendor_internal_article=vendor_internal_article)
    await state.set_state(create_order_state.insert_s_order)
    await callback.message.answer('Введите кол-во товара размера S:')


@router.message(create_order_state.insert_s_order)
async def insert_quantity_s(message: Message, state: FSMContext):
    try:
        quantity_s = int(message.text)
        await state.update_data(quantity_s=quantity_s)
        await state.set_state(create_order_state.insert_m_order)
        await message.answer('Введите кол-во товара размера M:')
    except ValueError:
        await message.answer('Введите целое число')


@router.message(create_order_state.insert_m_order)
async def insert_quantity_m(message: Message, state: FSMContext):
    try:
        quantity_m = int(message.text)
        await state.update_data(quantity_m=quantity_m)
        await state.set_state(create_order_state.insert_l_order)
        await message.answer('Введите кол-во товара размера L:')
    except ValueError:
        await message.answer('Введите целое число')


@router.message(create_order_state.insert_l_order)
async def insert_quantity_l(message: Message, state: FSMContext):
    try:
        quantity_l = int(message.text)
        await state.update_data(quantity_l=quantity_l)
        await state.set_state(create_order_state.insert_color)
        await message.answer('Введите цвет:')
    except ValueError:
        await message.answer('Введите целое число')


@router.message(create_order_state.insert_color)
async def insert_color(message: Message, state: FSMContext):
    try:
        color = str(message.text)
        await state.update_data(color=color)
        await state.set_state(create_order_state.insert_vendor_order)
        await message.answer('Введите название магазина:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_order_state.insert_vendor_order)
async def insert_vendor_name(message: Message, state: FSMContext):
    try:
        vendor_name = str(message.text)
        await state.update_data(vendor_name=vendor_name)
        await state.set_state(create_order_state.insert_sending_method)
        await message.answer('Введите тип отправки:', reply_markup=await kb.inline_sending_method())
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.callback_query(F.data.startswith('method_'), create_order_state.insert_sending_method)
async def choose_sending_method(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    sending_method = str(callback.data)
    await state.update_data(sending_method=sending_method[7:])
    await callback.message.answer('Прикрепите фотографию товара:')
    await state.set_state(create_order_state.insert_order_image_id)


@router.message(create_order_state.insert_order_image_id)
async def insert_image(message: Message, state: FSMContext):
    try:
        await state.update_data(order_image=message.photo[-1].file_id)
        date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        change_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        await state.update_data(date=date)
        await state.update_data(change_date=change_date)
        data = await state.get_data()
        await rq.create_order_db(data['internal_article'], data['quantity_s'], data['quantity_m'],
                                 data['quantity_l'], data['vendor_name'], data['sending_method'], data['order_image'],
                                 data['delivery_id'], data['color'], data['vendor_internal_article'], data['date'],
                                 data['change_date'])
        # order = await rq.get_order_test(data['order_image'])
        # json_str = '{"name": "John", "age": 30, "city": "New York"}'
        # await rq.set_sack_images(json_str, order.id)
        await message.answer('Заказ создан успешно')
        await state.clear()
    except TypeError:
        await message.answer('Ошибка, попробуйте еще раз')


"""Просмотр чеков + оплата------------------------------------------------------------------------------------------"""


@router.message(F.text == 'Просмотреть чеки')
async def get_cheques(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in senders:
        await message.answer('Выберите категорию чека:', reply_markup=kb.cheques_category)


@router.callback_query(F.data == 'all_chques')
async def get_all_cheques(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Список всех чеков', reply_markup=await kb.inline_all_cheques())


@router.callback_query(F.data == 'delay_cheques')
async def get_delay_cheques(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Список чеков с отсрочкой', reply_markup=await kb.inline_delay_cheques())


@router.callback_query(F.data == 'fire_cheques')
async def get_fire_cheques(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Список горящих чеков', reply_markup=await kb.inline_fire_cheques())


@router.callback_query(F.data.startswith('pay_cheque_'))
async def pay_cheques(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(change_cheque_status.select_cheque)
    cheque_id = str(callback.data)[11:]
    cheque = await rq.get_cheque(cheque_id)
    order = await rq.get_order(cheque.order_id)
    fish = await rq.get_fish_obj(cheque.order_id)
    await state.update_data(order_id=cheque.order_id, cheque_id=cheque.id)
    media_list = []
    if cheque.payment_image is None and order.fish is None:
        cheque_date_datetime = datetime.strptime(cheque.cheque_date, "%d-%m-%Y %H:%M")
        time_now = datetime.now()
        time = cheque_date_datetime + timedelta(days=14)
        days_left = time - time_now
        media_list.append(InputMediaPhoto(media=order.order_image_id, caption=
        f'*Кол-во дней до оплаты:* {days_left.days}\n', parse_mode="Markdown"))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Выберите действие', reply_markup=kb.select_cheque)
    elif order.fish is not None and cheque.payment_image is None:
        cheque_date_datetime = datetime.strptime(cheque.cheque_date, "%d-%m-%Y %H:%M")
        time_now = datetime.now()
        time = cheque_date_datetime + timedelta(days=14)
        days_left = time - time_now
        media_list.append(InputMediaPhoto(media=order.order_image_id, caption=
        f'*Кол-во дней до оплаты:* {days_left.days}\n', parse_mode="Markdown"))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=fish.fish_image_id))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Выберите действие:', reply_markup=kb.select_cheque)
    elif order.fish is not None and cheque.payment_image is not None:
        media_list.append(InputMediaPhoto(media=order.order_image_id))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=cheque.payment_image))
        media_list.append(InputMediaPhoto(media=fish.fish_image_id))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Вывести информацию:', reply_markup=kb.view_info)
    elif cheque.payment_image is not None:
        media_list.append(InputMediaPhoto(media=order.order_image_id))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=cheque.payment_image))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Вывести информацию:', reply_markup=kb.view_info)


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


"""Оплата чека------------------------------------------------------------------------------------------------------"""


@router.callback_query(F.data == 'pay_cheque', change_cheque_status.select_cheque)
async def pay_cheque(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(change_cheque_status.attach_pay_screen)
    await callback.message.answer('Пожалуйста прикрпите скрин оплаты:')


@router.message(change_cheque_status.attach_pay_screen)
async def insert_payment_image(message: Message, state: FSMContext):
    try:
        await state.update_data(pay_screen=message.photo[-1].file_id)
        cheque_status = 'Чек оплачен'
        await state.update_data(cheque_status=cheque_status)
        await state.update_data(cheque_date=datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        data = await state.get_data()
        await rq.set_payment_image(data['cheque_id'], data['pay_screen'])
        await rq.set_cheque_status(data['cheque_id'], data['cheque_status'], data['cheque_date'])
        await message.answer(f'Скрин оплаты прикреплен, статус чека изменен на {data["cheque_status"]}')
        await state.clear()
    except TypeError:
        await message.answer('Ошибка, попробуйте еще раз')


"""Просмотр заказов-------------------------------------------------------------------------------------------------"""


@router.message(F.text == 'Посмотреть заказы')
async def check_all_orders(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in senders:
        await message.answer('Выберите поставку:', reply_markup=await kb.all_incomes())


@router.callback_query(F.data.startswith('income_'))
async def check_income_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    income_id = str(callback.data)[7:]
    income_id = int(income_id)
    await callback.message.answer('Выберите заказ:', reply_markup=await kb.inline_all_orders_send(income_id))


@router.callback_query(F.data.startswith('get_info_'))
async def get_all_cheques(callback: CallbackQuery, state: FSMContext):
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
        await callback.message.answer('Вывести информацию:', reply_markup=kb.view_info)
    elif cheque.cheque_image_id is not None and order.fish is None and cheque.payment_image is None:
        await state.update_data(cheque_id=cheque.id)
        media_list.append(InputMediaPhoto(media=order.order_image_id))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Вывести информацию:', reply_markup=kb.view_info)
    elif cheque.payment_image is not None and order.fish is None and cheque.cheque_image_id is not None:
        await state.update_data(cheque_id=cheque.id)
        media_list.append(InputMediaPhoto(media=order.order_image_id))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=cheque.payment_image))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Вывести информацию:', reply_markup=kb.view_info)
    elif order.cheque_image_id is not None and cheque.payment_image is not None and order.fish is not None:
        await state.update_data(cheque_id=cheque.id)
        media_list.append(InputMediaPhoto(media=order.order_image_id))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=cheque.payment_image))
        media_list.append(InputMediaPhoto(media=fish.fish_image_id))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Вывести информацию:', reply_markup=kb.view_info)
    elif order.cheque_image_id is not None and cheque.payment_image is None and order.fish is not None:
        await state.update_data(cheque_id=cheque.id)
        media_list.append(InputMediaPhoto(media=order.order_image_id))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=fish.fish_image_id))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Вывести информацию:', reply_markup=kb.view_info)


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


"""Редактирование данных заказа-------------------------------------------------------------------------------------"""


@router.callback_query(F.data == 'edit_order', check_orders.select_order)
async def edit_order_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id in senders:
        await callback.answer()
        data = await state.get_data()
        await state.set_state(edit_orders.select_value)
        await state.update_data(order_id=data['order_id'])
        await callback.message.answer('Выберите поле для редактирования:', reply_markup=kb.choose_value)
    else:
        await callback.answer()
        await callback.message.answer('У вас нет доступа к данной функции')


@router.callback_query(F.data == 'edit_product_article', edit_orders.select_value)
async def edit_product_article_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Введите внутренний артикул товара:')
    await state.set_state(edit_orders.edit_product_article)


@router.message(edit_orders.edit_product_article)
async def edit_product_article_2(message: Message, state: FSMContext):
    try:
        product_article = str(message.text)
        await state.update_data(product_article=product_article)
        data = await state.get_data()
        await rq.edit_order_internal_article(data['order_id'], data['product_article'])
        await message.answer('Артикул успешно обновлен')
        await state.set_state(edit_orders.select_value)
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.callback_query(F.data == 'edit_vendor_article', edit_orders.select_value)
async def edit_vendor_article_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(edit_orders.edit_vendor_article)
    await callback.message.answer('Введите внутренний артикул поставщика:', reply_markup=kb.vendor_internal_article)


@router.message(edit_orders.edit_vendor_article)
async def edit_vendor_article_2(message: Message, state: FSMContext):
    try:
        vendor_article = str(message.text)
        await state.update_data(vendor_internal_article=vendor_article)
        data = await state.get_data()
        await rq.edit_order_vendor_internal_article(data['order_id'], data['vendor_internal_article'])
        await message.answer('Артикул успешно обновлен')
        await state.set_state(edit_orders.select_value)
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.callback_query(F.data == 'skip', edit_orders.edit_vendor_article)
async def skip_vendor_article(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    vendor_article = 'Не заполнено'
    await state.update_data(vendor_internal_article=vendor_article)
    data = await state.get_data()
    await rq.edit_order_vendor_internal_article(data['order_id'], data['vendor_internal_article'])
    await callback.message.answer('Артикул успешно обновлен')
    await state.set_state(edit_orders.select_value)


@router.callback_query(F.data == 'edit_s_quantity', edit_orders.select_value)
async def edit_s_quantity_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(edit_orders.edit_s_quantity)
    await callback.message.answer('Введите кол-во товара размера S:')


@router.message(edit_orders.edit_s_quantity)
async def edit_s_quantity_2(message: Message, state: FSMContext):
    try:
        quantity_s = int(message.text)
        if quantity_s >= 0:
            await state.update_data(quantity_s=quantity_s)
            data = await state.get_data()
            await rq.edit_order_s(data['order_id'], data['quantity_s'])
            await message.answer('Кол-во товара S успешно обновлено')
            await state.set_state(edit_orders.select_value)
        else:
            await message.answer('Значение не может быть меньше 0')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.callback_query(F.data == 'edit_m_quantity', edit_orders.select_value)
async def edit_m_quantity_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(edit_orders.edit_m_quantity)
    await callback.message.answer('Введите кол-во товара размера M:')


@router.message(edit_orders.edit_m_quantity)
async def edit_m_quantity_2(message: Message, state: FSMContext):
    try:
        quantity_m = int(message.text)
        if quantity_m >= 0:
            await state.update_data(quantity_m=quantity_m)
            data = await state.get_data()
            await rq.edit_order_m(data['order_id'], data['quantity_m'])
            await message.answer('Кол-во товара M успешно обновлено')
            await state.set_state(edit_orders.select_value)
        else:
            await message.answer('Значение не может быть меньше 0')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.callback_query(F.data == 'edit_l_quantity', edit_orders.select_value)
async def edit_l_quantity_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(edit_orders.edit_l_quantity)
    await callback.message.answer('Введите кол-во товара размера L:')


@router.message(edit_orders.edit_l_quantity)
async def edit_l_quantity_2(message: Message, state: FSMContext):
    try:
        quantity_l = int(message.text)
        if quantity_l >= 0:
            await state.update_data(quantity_l=quantity_l)
            data = await state.get_data()
            await rq.edit_order_l(data['order_id'], data['quantity_l'])
            await message.answer('Кол-во товара L успешно обновлено')
            await state.set_state(edit_orders.select_value)
        else:
            await message.answer('Значение не может быть меньше 0')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.callback_query(F.data == 'edit_color', edit_orders.select_value)
async def edit_color_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(edit_orders.edit_color)
    await callback.message.answer('Введите цвет:')


@router.message(edit_orders.edit_color)
async def edit_color_2(message: Message, state: FSMContext):
    try:
        color = str(message.text)
        await state.update_data(color=color)
        data = await state.get_data()
        await rq.edit_order_color(data['order_id'], data['color'])
        await message.answer('Цвет успешно обновлен')
        await state.set_state(edit_orders.select_value)
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.callback_query(F.data == 'edit_name', edit_orders.select_value)
async def edit_order_vendor_name_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(edit_orders.edit_name)
    await callback.message.answer('Введите название магазина:')


@router.message(edit_orders.edit_name)
async def edit_order_vendor_name_2(message: Message, state: FSMContext):
    try:
        name = str(message.text)
        await state.update_data(name=name)
        data = await state.get_data()
        await rq.edit_order_name(data['order_id'], data['name'])
        await message.answer('Название магазина успешно обновлено')
        await state.set_state(edit_orders.select_value)
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.callback_query(F.data == 'edit_sending_method', edit_orders.select_value)
async def edit_order_vendor_name_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(edit_orders.edit_sending_method)
    await callback.message.answer('Выберите тип отправки:', reply_markup=await kb.inline_sending_method())


@router.callback_query(F.data.startswith('method_'), edit_orders.edit_sending_method)
async def choose_sending_method(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    sending_method = str(callback.data)
    await state.update_data(sending_method=sending_method[7:])
    data = await state.get_data()
    await rq.edit_order_sending_method(data['order_id'], data['sending_method'])
    await callback.message.answer('Способ отправки успешно изменен')
    await state.set_state(edit_orders.select_value)
"""-----------------------------------------------------------------------------------------------------------------"""
