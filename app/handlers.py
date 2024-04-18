from datetime import datetime
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
    insert_cheque_number = State()
    insert_vendor_article = State()

    insert_fish = State()
    insert_fish_date = State()
    insert_fish_weight = State()
    insert_sack_count = State()
    insert_fish_image_id = State()


class change_cheque_status(StatesGroup):
    select_cheque = State()
    attach_pay_screen = State()


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
        await message.answer('Выберите заказ:', reply_markup=await kb.inline_all_orders())


@router.callback_query(F.data.startswith('edit_status_'))
async def edit_order_status_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(create_cheque_state.select_order)
    order_id = str(callback.data)[12:]
    await state.update_data(order_id=order_id)
    order = await rq.get_order(order_id)
    await state.set_state(create_cheque_state.select_status)
    await callback.message.answer_photo(caption=f'Id заказа {str(order.id)}\n'
                                                f'Дата создания заказа {str(order.date)}\n'
                                                f'Внутренний артикул {str(order.internal_article)}\n'
                                                f'Кол-во товара размера S {str(order.S)}\n'
                                                f'Кол-во товара размера M {str(order.M)}\n'
                                                f'Кол-во товара размера L {str(order.L)}\n'
                                                f'Название магазина {str(order.vendor_name)}\n'
                                                f'Способ отправки {str(order.sending_method)}\n'
                                                f'Статус заказа {str(order.order_status)}\n',
                                        photo=order.order_image_id,
                                        reply_markup=await kb.inline_order_status())


@router.callback_query(F.data.startswith('status_'), create_cheque_state.select_status)
async def edit_order_status_2(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    order_status = str(callback.data)[7:]
    data = await state.get_data()
    if order_status == 'Готов' and await rq.get_cheque(data['order_id']) is None:
        await state.update_data(order_status=order_status)
        await state.set_state(create_cheque_state.insert_date_cheque)
        await callback.message.answer('Внимание, чтобы поменить статус, нужно создать чек')
        await callback.message.answer('Введите дату, указанную на чеке(пример 2021-03-04 15:34):')
    elif (order_status == 'Передан в логистику' and await rq.get_fish(data['order_id']) is None
          and await rq.get_cheque(data['order_id']) is not None):
        await state.update_data(order_status=order_status)
        await state.set_state(create_cheque_state.insert_fish)
        await callback.message.answer('Внимание, чтобы поменить статус, нужно приложить FISH')
        await callback.message.answer('Введите номер FISH для данного заказа:')

    elif order_status == 'Передан в работу поставщику' and await rq.get_cheque(data['order_id']) is None:
        await state.update_data(order_status=order_status)
        data = await state.get_data()
        await rq.edit_order_status(data['order_id'], data['order_status'])
        await callback.message.answer('Статус успешно обновлен')
    else:
        await callback.message.answer('Нельзя выполнить действие')


@router.message(create_cheque_state.insert_date_cheque)
async def insert_vendor_cheque(message: Message, state: FSMContext):
    try:
        message_date = str(message.text)
        cheque_date = datetime.strptime(message_date, "%Y-%m-%d %H:%M")
        await state.update_data(cheque_date=cheque_date)
        await state.set_state(create_cheque_state.insert_cheque_number)
        await message.answer('Введите номер чека:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_cheque_number)
async def insert_price_cheque(message: Message, state: FSMContext):
    try:
        cheque_number = int(message.text)
        await state.update_data(cheque_number=cheque_number)
        await state.set_state(create_cheque_state.insert_vendor_article)
        await message.answer('Введите артикул поставщика:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_vendor_article)
async def insert_price_cheque(message: Message, state: FSMContext):
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
        data = await state.get_data()
        order = await rq.get_order(data['order_id'])
        await rq.create_cheque_db(order.vendor_name, data['price'], data['image'], data['order_id'],
                                  data['cheque_date'], data['cheque_number'], data['vendor_article'])
        await rq.edit_order_status(data['order_id'], data['order_status'])
        await rq.set_order_cheque_image(data['order_id'], data['image'])
        order = await rq.get_order(data['order_id'])
        await message.answer(f'Чек создан успешно\n'
                             f'Уникальный номер {order.sack_number}\n'
                             f'Данный номер нужно нанести на каждый мешок для поставки с артикулом {order.internal_article}'
                             )
        await message.answer(f'Статус заказа изменен на {data['order_status']}')
        await state.clear()
    except TypeError:
        await message.answer('Ошибка, попробуйте еще раз')


"""Создание fish----------------------------------------------------------------------------------------------------"""


@router.message(create_cheque_state.insert_fish)
async def insert_fish(message: Message, state: FSMContext):
    try:
        fish = int(message.text)
        await state.update_data(fish=fish)
        await state.set_state(create_cheque_state.insert_fish_date)
        await message.answer('Введите дату(пример 2023-03-03 23:23:23')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_fish_date)
async def insert_fish(message: Message, state: FSMContext):
    try:
        message_date = str(message.text)
        fish_date = datetime.strptime(message_date, "%Y-%m-%d %H:%M:%S")
        await state.update_data(fish_date=fish_date)
        await state.set_state(create_cheque_state.insert_fish_weight)
        await message.answer('Введите вес в кг:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_fish_weight)
async def insert_fish(message: Message, state: FSMContext):
    try:
        weight = int(message.text)
        await state.update_data(weight=weight)
        await state.set_state(create_cheque_state.insert_sack_count)
        await message.answer('Введите кол-во мешков:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_sack_count)
async def insert_fish(message: Message, state: FSMContext):
    try:
        sack_count = int(message.text)
        await state.update_data(sack_count=sack_count)
        await state.set_state(create_cheque_state.insert_fish_image_id)
        await message.answer('Прикрепите фотографию FISH:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_fish_image_id)
async def insert_fish(message: Message, state: FSMContext):
    try:
        await state.update_data(fish_image=message.photo[-1].file_id)
        data = await state.get_data()
        order = await rq.get_order(data['order_id'])
        await rq.create_fish(data['fish'], data['fish_date'], data['weight'], data['sack_count'], order.sending_method,
                             data['fish_image'], order.id)
        await rq.set_order_fish(data['order_id'], data['fish'])
        await rq.edit_order_status(data['order_id'], data['order_status'])
        await message.answer('FISH прикрплен')
        await message.answer(f'Статус заказа изменен на {data['order_status']}')
        await state.clear()
    except TypeError:
        await message.answer('Ошибка, попробуйте еще раз')


"""Проверка чеков---------------------------------------------------------------------------------------------------"""


@router.message(F.text == 'Проверить чеки')
async def edit_order_status(message: Message, state: FSMContext):
    if message.from_user.id in recipients:
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
    fish_scalar = await rq.get_fish(order.fish)
    await state.update_data(order_id=cheque.order_id, cheque_id=cheque.id)
    media_list = []
    if cheque.payment_image is None:
        media_list.append(InputMediaPhoto(media=order.order_image_id, caption=
        f'Id заказа {str(order.id)}\n'
        f'Дата создания заказа {str(order.date)}\n'
        f'Внутренний артикул {str(order.internal_article)}\n'
        f'Кол-во товара размера S {str(order.S)}\n'
        f'Кол-во товара размера M {str(order.M)}\n'
        f'Кол-во товара размера L {str(order.L)}\n'
        f'Название магазина {str(order.vendor_name)}\n'
        f'Способ отправки {str(order.sending_method)}\n'
        f'Статус заказа {str(order.order_status)}\n'
        f'ID чека {str(cheque.id)}\n'
        f'Дата последнего изменения чека {str(cheque.date)}\n'
        f'Дата чека {str(cheque.cheque_date)}\n'
        f'Название магазина {str(cheque.vendor_name)}\n'
        f'Цена {str(cheque.price)}\n'
        f'Статус чека {str(cheque.cheque_status)}\n'))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        await callback.message.answer_media_group(media=media_list)
    elif order.fish is not None and cheque.payment_image is not None:
        media_list.append(InputMediaPhoto(media=order.order_image_id, caption=
        f'Id заказа {str(order.id)}\n'
        f'Дата создания заказа {str(order.date)}\n'
        f'Внутренний артикул {str(order.internal_article)}\n'
        f'Кол-во товара размера S {str(order.S)}\n'
        f'Кол-во товара размера M {str(order.M)}\n'
        f'Кол-во товара размера L {str(order.L)}\n'
        f'Название магазина {str(order.vendor_name)}\n'
        f'Способ отправки {str(order.sending_method)}\n'
        f'Статус заказа {str(order.order_status)}\n'
        f'FISH номер заказа {str(order.fish)}\n'
        f'ID чека {str(cheque.id)}\n'
        f'Дата последнего изменения чека {str(cheque.date)}\n'
        f'Дата чека {str(cheque.cheque_date)}\n'
        f'Название магазина {str(cheque.vendor_name)}\n'
        f'Цена {str(cheque.price)}\n'
        f'Статус чека {str(cheque.cheque_status)}\n'))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=cheque.payment_image))
        media_list.append(InputMediaPhoto(media=fish_scalar.fish_image_id))
        await callback.message.answer_media_group(media=media_list)
    elif cheque.payment_image is not None:
        media_list.append(InputMediaPhoto(media=order.order_image_id, caption=
        f'Id заказа {str(order.id)}\n'
        f'Дата создания заказа {str(order.date)}\n'
        f'Внутренний артикул {str(order.internal_article)}\n'
        f'Кол-во товара размера S {str(order.S)}\n'
        f'Кол-во товара размера M {str(order.M)}\n'
        f'Кол-во товара размера L {str(order.L)}\n'
        f'Название магазина {str(order.vendor_name)}\n'
        f'Способ отправки {str(order.sending_method)}\n'
        f'Статус заказа {str(order.order_status)}\n'
        f'ID чека {str(cheque.id)}\n'
        f'Дата последнего изменения чека {str(cheque.date)}\n'
        f'Дата чека {str(cheque.cheque_date)}\n'
        f'Название магазина {str(cheque.vendor_name)}\n'
        f'Цена {str(cheque.price)}\n'
        f'Статус чека {str(cheque.cheque_status)}\n'))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=cheque.payment_image))
        await callback.message.answer_media_group(media=media_list)


"""Создание заказа--------------------------------------------------------------------------------------------------"""


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


"""Просмотр чеков + оплата------------------------------------------------------------------------------------------"""


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
    fish_scalar = await rq.get_fish(cheque.order_id)
    await state.update_data(order_id=cheque.order_id, cheque_id=cheque.id)
    media_list = []
    if cheque.payment_image is None:
        media_list.append(InputMediaPhoto(media=order.order_image_id, caption=
        f'Id заказа {str(order.id)}\n'
        f'Дата создания заказа {str(order.date)}\n'
        f'Внутренний артикул {str(order.internal_article)}\n'
        f'Кол-во товара размера S {str(order.S)}\n'
        f'Кол-во товара размера M {str(order.M)}\n'
        f'Кол-во товара размера L {str(order.L)}\n'
        f'Название магазина {str(order.vendor_name)}\n'
        f'Способ отправки {str(order.sending_method)}\n'
        f'Статус заказа {str(order.order_status)}\n'
        f'ID чека {str(cheque.id)}\n'
        f'Дата последнего изменения чека {str(cheque.date)}\n'
        f'Дата чека {str(cheque.cheque_date)}\n'
        f'Название магазина {str(cheque.vendor_name)}\n'
        f'Цена {str(cheque.price)}\n'
        f'Статус чека {str(cheque.cheque_status)}\n'))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Выберите действие', reply_markup=kb.select_cheque)
    elif order.order_status == 'Передан в логистику' and cheque.payment_image is not None:
        media_list.append(InputMediaPhoto(media=order.order_image_id, caption=
        f'Id заказа {str(order.id)}\n'
        f'Дата создания заказа {str(order.date)}\n'
        f'Внутренний артикул {str(order.internal_article)}\n'
        f'Кол-во товара размера S {str(order.S)}\n'
        f'Кол-во товара размера M {str(order.M)}\n'
        f'Кол-во товара размера L {str(order.L)}\n'
        f'Название магазина {str(order.vendor_name)}\n'
        f'Способ отправки {str(order.sending_method)}\n'
        f'Статус заказа {str(order.order_status)}\n'
        f'FISH номер заказа {str(order.fish)}\n'
        f'ID чека {str(cheque.id)}\n'
        f'Дата последнего изменения чека {str(cheque.date)}\n'
        f'Дата чека {str(cheque.cheque_date)}\n'
        f'Название магазина {str(cheque.vendor_name)}\n'
        f'Цена {str(cheque.price)}\n'
        f'Статус чека {str(cheque.cheque_status)}\n'))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=fish_scalar.fish_image_id))
        await callback.message.answer_media_group(media=media_list)
    elif cheque.payment_image is not None:
        media_list.append(InputMediaPhoto(media=order.order_image_id, caption=
        f'Id заказа {str(order.id)}\n'
        f'Дата создания заказа {str(order.date)}\n'
        f'Внутренний артикул {str(order.internal_article)}\n'
        f'Кол-во товара размера S {str(order.S)}\n'
        f'Кол-во товара размера M {str(order.M)}\n'
        f'Кол-во товара размера L {str(order.L)}\n'
        f'Название магазина {str(order.vendor_name)}\n'
        f'Способ отправки {str(order.sending_method)}\n'
        f'Статус заказа {str(order.order_status)}\n'
        f'ID чека {str(cheque.id)}\n'
        f'Дата последнего изменения чека {str(cheque.date)}\n'
        f'Дата чека {cheque.cheque_date}'
        f'Название магазина {str(cheque.vendor_name)}\n'
        f'Цена {str(cheque.price)}\n'
        f'Статус чека {str(cheque.cheque_status)}\n'))
        media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
        media_list.append(InputMediaPhoto(media=cheque.payment_image))
        await callback.message.answer_media_group(media=media_list)


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
        await state.update_data(cheque_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        data = await state.get_data()
        await rq.set_payment_image(data['cheque_id'], data['pay_screen'])
        await rq.set_cheque_status(data['cheque_id'], data['cheque_status'], data['cheque_date'])
        await message.answer(f'Скрин оплаты прикреплен, статус чека изменен на {data['cheque_status']}')
        await state.clear()
    except TypeError:
        await message.answer('Ошибка, попробуйте еще раз')
