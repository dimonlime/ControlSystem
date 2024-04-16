from datetime import datetime
import json

import aiogram.utils.magic_filter
from aiogram import types, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.id_config import senders, recipients
from app import keyboards as kb
from app.database import requests as rq

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


class create_cheque_state(StatesGroup):
    select_order = State()
    select_status = State()
    attach_cheque_image = State()
    insert_date_cheque = State()
    insert_vendor_cheque = State()
    insert_price_cheque = State()
    insert_image_cheque = State()
    insert_fish = State()


class change_cheque_status(StatesGroup):
    select_cheque = State()
    attach_pay_screen = State()


@router.message(CommandStart())
async def start(message: Message):
    if message.from_user.id in senders:
        print(message.from_user.id)
        await message.answer(
            f'{message.from_user.first_name} добро пожаловать, вы авторизованы как отправляющая сторона',
            reply_markup=kb.sender_keyboard)
    elif message.from_user.id in recipients:
        print(message.from_user.id)
        await message.answer(
            f'{message.from_user.first_name} добро пожаловать, вы авторизованы как принимающая сторона',
            reply_markup=kb.recipient_keyboard)


"""-----------------------------------------------------------------------------------------------------------------"""


@router.message(F.text == 'Изменить статус заказа')
async def edit_order_status(message: Message, state: FSMContext):
    if message.from_user.id in recipients:
        await message.answer('Выберите заказ:', reply_markup=await kb.inline_all_orders())


@router.callback_query(F.data.startswith('edit_status_'))
async def edit_order_status_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(create_cheque_state.select_order)
    order_id = str(callback.data)[12:]
    await state.update_data(order_id=order_id)
    await state.set_state(create_cheque_state.select_status)
    await callback.message.answer('Выберите статус:', reply_markup=await kb.inline_order_status())


@router.callback_query(F.data.startswith('status_'), create_cheque_state.select_status)
async def edit_order_status_2(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    order_status = str(callback.data)[7:]
    data = await state.get_data()
    if order_status == 'Готов' and await rq.get_cheque(data['order_id']) is None:
        await state.update_data(order_status=order_status)
        await state.set_state(create_cheque_state.insert_vendor_cheque)
        await callback.message.answer('Внимание, чтобы поменить статус, нужно создать чек')
        await callback.message.answer('Введите название магазина:')
    elif (order_status == 'Передан в логистику' and await rq.get_fish(data['order_id']) is None
          and await rq.get_cheque(data['order_id']) is not None):
        await state.update_data(order_status=order_status)
        await state.set_state(create_cheque_state.insert_fish)
        await callback.message.answer('Внимание, чтобы поменить статус, нужно приложить FISH')
        await callback.message.answer('Введите FISH для данного заказа:')

    elif order_status == 'Передан в работу поставщику' and await rq.get_cheque(data['order_id']) is None:
        await state.update_data(order_status=order_status)
        data = await state.get_data()
        await rq.edit_order_status(data['order_id'], data['order_status'])
        await callback.message.answer('Статус успешно обновлен')
    else:
        await callback.message.answer('Нельзя выполнить действие')


@router.message(create_cheque_state.insert_fish)
async def insert_fish(message: Message, state: FSMContext):
    try:
        fish = str(message.text)
        await state.update_data(fish=fish)
        data = await state.get_data()
        await rq.set_order_fish(data['order_id'], data['fish'])
        await rq.edit_order_status(data['order_id'], data['order_status'])
        await message.answer('FISH прикрплен')
        await message.answer(f'Статус заказа изменен на {data['order_status']}')
        await state.clear()
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_vendor_cheque)
async def insert_vendor_cheque(message: Message, state: FSMContext):
    try:
        vendor_name = str(message.text)
        await state.update_data(vendor_name=vendor_name)
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
        data = await state.get_data()
        await rq.create_cheque_db(data['vendor_name'], data['price'], data['image'], data['order_id'])
        await rq.edit_order_status(data['order_id'], data['order_status'])
        await rq.set_order_cheque_image(data['order_id'], data['image'])
        await message.answer('Чек создан успешно')
        await message.answer(f'Статус заказа изменен на {data['order_status']}')
        await state.clear()
    except TypeError:
        await message.answer('Ошибка, попробуйте еще раз')


"""-----------------------------------------------------------------------------------------------------------------"""


@router.message(F.text == 'Проверить чеки')
async def edit_order_status(message: Message, state: FSMContext):
    await message.answer('Выберите категорию чека:', reply_markup=kb.cheques_category_2)


@router.callback_query(F.data == 'paid_cheques')
async def get_unpaid_cheques(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Список оплаченных чеков', reply_markup=await kb.inline_paid_cheques())


@router.callback_query(F.data == 'unpaid_cheques')
async def get_unpaid_cheques(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Список не оплаченных чеков', reply_markup=await kb.inline_unpaid_cheques())


@router.callback_query(F.data.startswith('view_cheque_'))
async def insert_date_cheque(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(change_cheque_status.select_cheque)
    cheque_id = str(callback.data)[12:]
    cheque = await rq.get_cheque(cheque_id)
    order = await rq.get_order(cheque.order_id)
    await state.update_data(order_id=cheque.order_id, cheque_id=cheque.id)
    if cheque.payment_image is None:
        await callback.message.answer_photo(caption=f'Id заказа {str(order.id)}\n'
                                                    f'Дата заказа {str(order.date)}\n'
                                                    f'Внутренний артикул {str(order.internal_article)}\n'
                                                    f'Кол-во товара размера S {str(order.S)}\n'
                                                    f'Кол-во товара размера M {str(order.M)}\n'
                                                    f'Кол-во товара размера L {str(order.L)}\n'
                                                    f'Название магазина {str(order.vendor_name)}\n'
                                                    f'Способ отправки {str(order.sending_method)}\n'
                                                    f'Статус заказа {str(order.order_status)}\n',
                                            photo=order.order_image_id)
        await callback.message.answer_photo(caption=f'ID чека {str(cheque.id)}\n'
                                                    f'Дата чека {str(cheque.date)}\n'
                                                    f'Название магазина {str(cheque.vendor_name)}\n'
                                                    f'Цена {str(cheque.price)}\n'
                                                    f'Статус чека {str(cheque.cheque_status)}\n',
                                            photo=cheque.cheque_image_id)
    elif order.fish is not None and cheque.payment_image is not None:
        await callback.message.answer_photo(caption=f'Id заказа {str(order.id)}\n'
                                                    f'Дата заказа {str(order.date)}\n'
                                                    f'Внутренний артикул {str(order.internal_article)}\n'
                                                    f'Кол-во товара размера S {str(order.S)}\n'
                                                    f'Кол-во товара размера M {str(order.M)}\n'
                                                    f'Кол-во товара размера L {str(order.L)}\n'
                                                    f'Название магазина {str(order.vendor_name)}\n'
                                                    f'Способ отправки {str(order.sending_method)}\n'
                                                    f'Статус заказа {str(order.order_status)}\n'
                                                    f'FISH номер заказа {str(order.fish)}\n',
                                            photo=order.order_image_id)
        await callback.message.answer_photo(caption=f'ID чека {str(cheque.id)}\n'
                                                    f'Дата чека {str(cheque.date)}\n'
                                                    f'Название магазина {str(cheque.vendor_name)}\n'
                                                    f'Цена {str(cheque.price)}\n'
                                                    f'Статус чека {str(cheque.cheque_status)}\n',
                                            photo=cheque.cheque_image_id)
        await callback.message.answer_photo(caption='Скрин оплаты', photo=cheque.payment_image)
    elif cheque.payment_image is not None:
        await callback.message.answer_photo(caption=f'Id заказа {str(order.id)}\n'
                                                    f'Дата заказа {str(order.date)}\n'
                                                    f'Внутренний артикул {str(order.internal_article)}\n'
                                                    f'Кол-во товара размера S {str(order.S)}\n'
                                                    f'Кол-во товара размера M {str(order.M)}\n'
                                                    f'Кол-во товара размера L {str(order.L)}\n'
                                                    f'Название магазина {str(order.vendor_name)}\n'
                                                    f'Способ отправки {str(order.sending_method)}\n'
                                                    f'Статус заказа {str(order.order_status)}\n',
                                            photo=order.order_image_id)
        await callback.message.answer_photo(caption=f'ID чека {str(cheque.id)}\n'
                                                    f'Дата чека {str(cheque.date)}\n'
                                                    f'Название магазина {str(cheque.vendor_name)}\n'
                                                    f'Цена {str(cheque.price)}\n'
                                                    f'Статус чека {str(cheque.cheque_status)}\n',
                                            photo=cheque.cheque_image_id)
        await callback.message.answer_photo(caption='Скрин оплаты', photo=cheque.payment_image)


"""-----------------------------------------------------------------------------------------------------------------"""


@router.message(F.text == 'Создать заказ')
async def create_cheque(message: Message, state: FSMContext):
    if message.from_user.id in senders:
        await state.set_state(create_order_state.insert_internal_article)
        await message.answer('Введите внутренний артикул товара:')


@router.message(create_order_state.insert_internal_article)
async def insert_date_cheque(message: Message, state: FSMContext):
    try:
        internal_article = str(message.text)
        await state.update_data(internal_article=internal_article)
        await state.set_state(create_order_state.insert_s_order)
        await message.answer('Введите кол-во товара размера S:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_order_state.insert_s_order)
async def insert_date_cheque(message: Message, state: FSMContext):
    try:
        quantity_s = int(message.text)
        await state.update_data(quantity_s=quantity_s)
        await state.set_state(create_order_state.insert_m_order)
        await message.answer('Введите кол-во товара размера M:')
    except ValueError:
        await message.answer('Введите целое число')


@router.message(create_order_state.insert_m_order)
async def insert_date_cheque(message: Message, state: FSMContext):
    try:
        quantity_m = int(message.text)
        await state.update_data(quantity_m=quantity_m)
        await state.set_state(create_order_state.insert_l_order)
        await message.answer('Введите кол-во товара размера L:')
    except ValueError:
        await message.answer('Введите целое число')


@router.message(create_order_state.insert_l_order)
async def insert_date_cheque(message: Message, state: FSMContext):
    try:
        quantity_l = int(message.text)
        await state.update_data(quantity_l=quantity_l)
        await state.set_state(create_order_state.insert_vendor_order)
        await message.answer('Введите название магазина:')
    except ValueError:
        await message.answer('Введите целое число')


@router.message(create_order_state.insert_vendor_order)
async def insert_date_cheque(message: Message, state: FSMContext):
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
async def insert_date_cheque(message: Message, state: FSMContext):
    try:
        await state.update_data(order_image=message.photo[-1].file_id)
        data = await state.get_data()
        await rq.create_order_db(data['internal_article'], data['quantity_s'], data['quantity_m'],
                                 data['quantity_l'], data['vendor_name'], data['sending_method'], data['order_image'])
        await message.answer('Заказ создан успешно')
        await state.clear()
    except TypeError:
        await message.answer('Ошибка, попробуйте еще раз')


"""-----------------------------------------------------------------------------------------------------------------"""


@router.message(F.text == 'Просмотреть чеки')
async def create_cheque(message: Message, state: FSMContext):
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
async def insert_date_cheque(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(change_cheque_status.select_cheque)
    cheque_id = str(callback.data)[11:]
    cheque = await rq.get_cheque(cheque_id)
    order = await rq.get_order(cheque.order_id)
    await state.update_data(order_id=cheque.order_id, cheque_id=cheque.id)
    if cheque.payment_image is None:
        await callback.message.answer_photo(caption=f'Id заказа {str(order.id)}\n'
                                                    f'Дата заказа {str(order.date)}\n'
                                                    f'Внутренний артикул {str(order.internal_article)}\n'
                                                    f'Кол-во товара размера S {str(order.S)}\n'
                                                    f'Кол-во товара размера M {str(order.M)}\n'
                                                    f'Кол-во товара размера L {str(order.L)}\n'
                                                    f'Название магазина {str(order.vendor_name)}\n'
                                                    f'Способ отправки {str(order.sending_method)}\n'
                                                    f'Статус заказа {str(order.order_status)}\n',
                                            photo=order.order_image_id)
        await callback.message.answer_photo(caption=f'ID чека {str(cheque.id)}\n'
                                                    f'Дата чека {str(cheque.date)}\n'
                                                    f'Название магазина {str(cheque.vendor_name)}\n'
                                                    f'Цена {str(cheque.price)}\n'
                                                    f'Статус чека {str(cheque.cheque_status)}\n',
                                            photo=cheque.cheque_image_id, reply_markup=kb.select_cheque)
    elif order.order_status == 'Передан в логистику' and cheque.payment_image is not None:
        await callback.message.answer_photo(caption=f'Id заказа {str(order.id)}\n'
                                                    f'Дата заказа {str(order.date)}\n'
                                                    f'Внутренний артикул {str(order.internal_article)}\n'
                                                    f'Кол-во товара размера S {str(order.S)}\n'
                                                    f'Кол-во товара размера M {str(order.M)}\n'
                                                    f'Кол-во товара размера L {str(order.L)}\n'
                                                    f'Название магазина {str(order.vendor_name)}\n'
                                                    f'Способ отправки {str(order.sending_method)}\n'
                                                    f'Статус заказа {str(order.order_status)}\n'
                                                    f'FISH номер заказа {str(order.fish)}\n',
                                            photo=order.order_image_id)
        await callback.message.answer_photo(caption=f'ID чека {str(cheque.id)}\n'
                                                    f'Дата чека {str(cheque.date)}\n'
                                                    f'Название магазина {str(cheque.vendor_name)}\n'
                                                    f'Цена {str(cheque.price)}\n'
                                                    f'Статус чека {str(cheque.cheque_status)}\n',
                                            photo=cheque.cheque_image_id)
        await callback.message.answer_photo(caption='Скрин оплаты', photo=cheque.payment_image)
    elif cheque.payment_image is not None:
        await callback.message.answer_photo(caption=f'Id заказа {str(order.id)}\n'
                                                    f'Дата заказа {str(order.date)}\n'
                                                    f'Внутренний артикул {str(order.internal_article)}\n'
                                                    f'Кол-во товара размера S {str(order.S)}\n'
                                                    f'Кол-во товара размера M {str(order.M)}\n'
                                                    f'Кол-во товара размера L {str(order.L)}\n'
                                                    f'Название магазина {str(order.vendor_name)}\n'
                                                    f'Способ отправки {str(order.sending_method)}\n'
                                                    f'Статус заказа {str(order.order_status)}\n',
                                            photo=order.order_image_id)
        await callback.message.answer_photo(caption=f'ID чека {str(cheque.id)}\n'
                                                    f'Дата чека {str(cheque.date)}\n'
                                                    f'Название магазина {str(cheque.vendor_name)}\n'
                                                    f'Цена {str(cheque.price)}\n'
                                                    f'Статус чека {str(cheque.cheque_status)}\n',
                                            photo=cheque.cheque_image_id)
        await callback.message.answer_photo(caption='Скрин оплаты', photo=cheque.payment_image)


@router.callback_query(F.data == 'pay_cheque', change_cheque_status.select_cheque)
async def get_all_cheques(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(change_cheque_status.attach_pay_screen)
    await callback.message.answer('Пожалуйста прикрпите скрин оплаты:')


@router.message(change_cheque_status.attach_pay_screen)
async def insert_date_cheque(message: Message, state: FSMContext):
    try:
        await state.update_data(pay_screen=message.photo[-1].file_id)
        cheque_status = 'Чек оплачен'
        await state.update_data(cheque_status=cheque_status)
        data = await state.get_data()
        await rq.set_payment_image(data['cheque_id'], data['pay_screen'])
        await rq.set_cheque_status(data['cheque_id'], data['cheque_status'])
        await message.answer(f'Скрин оплаты прикреплен, статус чека изменен на {data['cheque_status']}')
        await state.clear()
    except TypeError:
        await message.answer('Ошибка, попробуйте еще раз')
