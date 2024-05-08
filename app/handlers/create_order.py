from datetime import datetime
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.id_config import senders
from app.keyboards import async_keyboards as async_kb
from app.keyboards import static_keyboards as static_kb
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
    insert_delivery_id = State()
    insert_color = State()
    insert_vendor_internal_article = State()


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





