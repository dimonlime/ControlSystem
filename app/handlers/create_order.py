from datetime import datetime
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from app.id_config import senders
from app.keyboards import async_keyboards as async_kb
from app.keyboards import static_keyboards as static_kb
from app.database import requests as rq
from app.utils.utils import check_article_image

from app.states.create_order import create_order_state

router = Router()


"""Создание заказа--------------------------------------------------------------------------------------------------"""


@router.message(F.text == 'Создать заказ')
async def create_order(message: Message, state: FSMContext):
    if message.from_user.id in senders:
        await state.set_state(create_order_state.insert_delivery_id)
        await message.answer('Введите ID поставки к которой относится заказ, либо выберите существующую:',
                             reply_markup=await async_kb.all_incomes())


@router.message(create_order_state.insert_delivery_id)
async def insert_delivery_id(message: Message, state: FSMContext):
    try:
        delivery_id = int(message.text)
        if delivery_id > 0:
            await state.update_data(delivery_id=delivery_id)
            await state.set_state(create_order_state.insert_delivery_date)
            await message.answer(f'Введите дату поставки, либо оставьте текующую({datetime.now().strftime("%d-%m-%Y")})'
                                 f', пример: 04-04-2024', reply_markup=static_kb.delivery_date)
        else:
            await message.answer('ID поставки не может быть меньше нуля...')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.callback_query(F.data.startswith('income_all_'), create_order_state.insert_delivery_id)
async def check_income_order(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        delivery_id_raw = str(callback.data)[11:]
        delivery_id = int(delivery_id_raw)
        delivery_date = await rq.get_delivery_date_by_del_id(delivery_id)
        await state.update_data(delivery_id=delivery_id)
        await state.update_data(delivery_date=delivery_date)
        await state.set_state(create_order_state.insert_internal_article)
        await callback.message.answer('Введите внутренний артикул товара:')
    except ValueError:
        await callback.message.answer('Ошибка, попробуйте еще раз')


@router.message(create_order_state.insert_delivery_date)
async def insert_delivery_id(message: Message, state: FSMContext):
    try:
        delivery_date = str(message.text)
        delivery_date_time = datetime.strptime(delivery_date, "%d-%m-%Y")
        await state.update_data(delivery_date=delivery_date)
        await state.set_state(create_order_state.insert_internal_article)
        await message.answer('Введите внутренний артикул товара:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.callback_query(F.data == 'today_date', create_order_state.insert_delivery_date)
async def check_income_order(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        delivery_date = datetime.now().strftime("%d-%m-%Y")
        await state.update_data(delivery_date=delivery_date)
        await state.set_state(create_order_state.insert_internal_article)
        await callback.message.answer('Введите внутренний артикул товара:')
    except ValueError:
        await callback.message.answer('Ошибка, попробуйте еще раз')


@router.message(create_order_state.insert_internal_article)
async def insert_internal_article(message: Message, state: FSMContext):
    try:
        internal_article = str(message.text)
        await state.update_data(internal_article=internal_article)
        await state.set_state(create_order_state.insert_vendor_internal_article)
        await message.answer('Введите внутренний артикул поставщика:', reply_markup=static_kb.vendor_internal_article)
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
        await message.answer('Введите тип отправки:', reply_markup=await async_kb.inline_sending_method())
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.callback_query(F.data.startswith('method_'), create_order_state.insert_sending_method)
async def choose_sending_method(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    sending_method = str(callback.data)
    await state.update_data(sending_method=sending_method[7:])
    data = await state.get_data()
    order_image = await check_article_image(data['internal_article'])
    if order_image is not None:
        await state.update_data(order_image=order_image)
        await state.set_state(create_order_state.create_order)
        await insert_image_auto(callback.message, state)
    else:
        await callback.message.answer('Прикрепите фотографию товара:')
        await state.set_state(create_order_state.insert_order_image_id)


@router.message(create_order_state.create_order)
async def insert_image_auto(message: Message, state: FSMContext):
    date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    change_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    await state.update_data(date=date)
    await state.update_data(change_date=change_date)
    data = await state.get_data()
    await rq.create_order_db(data['internal_article'], data['quantity_s'], data['quantity_m'],
                             data['quantity_l'], data['vendor_name'], data['sending_method'], data['order_image'],
                             data['delivery_id'], data['color'], data['vendor_internal_article'], data['date'],
                             data['change_date'], data['delivery_date'])
    # order = await rq.get_order_test(data['order_image'])
    # json_str = '{"name": "John", "age": 30, "city": "New York"}'
    # await rq.set_sack_images(json_str, order.id)
    await message.answer('Заказ создан успешно')
    for chat_id in senders:
        if chat_id != message.chat.id:
            media_list = [InputMediaPhoto(media=data['order_image'], caption=f'🔴Оповещение о создании заказа🔴\n'
                                                                             f'Артикул: {data['internal_article']}\n'
                                                                             f'Дата создания заказа: {data['date']}\n'
                                                                             f'Кол-во товара S: {data['quantity_s']}\n'
                                                                             f'Кол-во товара M: {data['quantity_m']}\n'
                                                                             f'Кол-во товара L: {data['quantity_l']}\n')]
            await message.bot.send_media_group(media=media_list, chat_id=chat_id)
    await state.clear()


@router.message(create_order_state.insert_order_image_id)
async def insert_image(message: Message, state: FSMContext):
    try:
        await state.update_data(order_image=message.photo[-1].file_id)
        date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        change_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        await state.update_data(date=date)
        await state.update_data(change_date=change_date)
        data = await state.get_data()
        await rq.create_article(data['internal_article'], data['order_image'])
        await rq.create_order_db(data['internal_article'], data['quantity_s'], data['quantity_m'],
                                 data['quantity_l'], data['vendor_name'], data['sending_method'], data['order_image'],
                                 data['delivery_id'], data['color'], data['vendor_internal_article'], data['date'],
                                 data['change_date'], data['delivery_date'])
        # order = await rq.get_order_test(data['order_image'])
        # json_str = '{"name": "John", "age": 30, "city": "New York"}'
        # await rq.set_sack_images(json_str, order.id)
        await message.answer('Заказ создан успешно')
        for chat_id in senders:
            if chat_id != message.chat.id:
                media_list = [InputMediaPhoto(media=data['order_image'], caption=f'🔴Оповещение о создании заказа🔴\n'
                                                                                 f'Артикул: {data['internal_article']}\n'
                                                                                 f'Дата создания заказа: {data['date']}\n'
                                                                                 f'Кол-во товара S: {data['quantity_s']}\n'
                                                                                 f'Кол-во товара M: {data['quantity_m']}\n'
                                                                                 f'Кол-во товара L: {data['quantity_l']}\n')]
                await message.bot.send_media_group(media=media_list, chat_id=chat_id)
        await state.clear()
    except TypeError:
        await message.answer('Ошибка, попробуйте еще раз')

