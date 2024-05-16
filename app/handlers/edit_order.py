from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.id_config import senders
from app.keyboards import async_keyboards as async_kb
from app.keyboards import static_keyboards as static_kb
from app.database import requests as rq

from app.states.edit_order import edit_orders
from app.states.check_order import check_orders

router = Router()


"""Редактирование данных заказа-------------------------------------------------------------------------------------"""


@router.callback_query(F.data == 'edit_order')
async def edit_order_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id in senders and await state.get_state() == check_orders.select_order:
        await callback.answer()
        data = await state.get_data()
        order = await rq.get_order(data['order_id'])
        if order.order_status == 'Заказ создан':
            await state.set_state(edit_orders.select_value)
            await state.update_data(order_id=data['order_id'])
            await callback.message.answer('Выберите поле для редактирования:', reply_markup=static_kb.choose_value)
        else:
            await callback.message.answer(f'Нельзя редактировать заказ, статус "{order.order_status}"')
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
    await callback.message.answer('Введите внутренний артикул поставщика:',
                                  reply_markup=static_kb.vendor_internal_article)


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
    await callback.message.answer('Выберите тип отправки:', reply_markup=await async_kb.inline_sending_method())


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
