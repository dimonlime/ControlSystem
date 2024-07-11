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

router = Router()


@router.message(F.text == 'Текущие заказы')
async def check_all_orders(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in senders:
        await state.set_state(check_orders.select_order)
        await message.answer('Выберите заказ:', reply_markup=await async_kb.all_orders())


@router.callback_query(F.data.startswith('order_id_'), check_orders.select_order)
async def check_income_order_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    order_id = str(callback.data)[9:]
    order = await order_rq.get_order(order_id)
    await state.update_data(order=order, callback=callback, state=state)
    ship_s = await shipments_quantity_s(order_id)
    ship_m = await shipments_quantity_m(order_id)
    ship_l = await shipments_quantity_l(order_id)
    order_create_date = datetime.strptime(order.create_date, "%d-%m-%Y %H:%M:%S")
    caption = ''
    if order.flag:
        caption += f'🚩 *Заказ отмечен*\n'
    caption += (f'*Артикул:* _{order.internal_article}_\n'
               f'*Дата создания заказа:* _{datetime.strftime(order_create_date, "%d-%m-%Y %H:%M")}_\n'
               f'*Цвет:* _{order.color}_\n'
               f'*Название магазина:* _{order.shop_name}_\n'
               f'*Способ отправки:* _{order.sending_method}_\n'
               f'*Заказано:* *S:* _{order.quantity_s}_ *M:* _{order.quantity_m}_ *L:* _{order.quantity_l}_\n'
               f'*Отправлено:* *S:* _{ship_s}_ *M:* _{ship_m}_ *L:* _{ship_l}_\n')
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
    await callback.message.answer(f'Выберите действие', reply_markup=static_kb.active_order_actions)


@router.callback_query(F.data.startswith('all_data_shipment'))
async def check_income_order_2(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    shipment = data['shipment']
    cheque = await cheque_rq.get_cheque(shipment.id)
    fish = await fish_rq.get_fish(shipment.id)
    text = (f'------Данные поставки------\n'
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
    await callback.message.answer(text, parse_mode="Markdown")


@router.callback_query(F.data.startswith('all_data_order'))
async def check_income_order_3(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    order = data['order']
    text = (f'------Данные заказа------\n'
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
    await callback.message.answer(text, parse_mode="Markdown")


@router.callback_query(F.data == 'close_order')
async def check_income_order_4(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    # if not await shipments_ready(data['order'].id):
    #     await callback.message.answer('*Нельзя отправить заказ в архив, т.к не все поставки приняты на складе WB*', parse_mode='Markdown')
    # else:
    await state.set_state(check_orders.close_order)
    await callback.message.answer(f'*Не отправлено S:* _{data["remain_s"]}_ *M:* _{data["remain_m"]}_ *L:* _{data["remain_l"]}_\n'
                                      f'*Вы уверены, что хотите отправить заказ в архив?*', reply_markup=static_kb.close_order, parse_mode='Markdown')


@router.callback_query(F.data == 'send_to_archive', check_orders.close_order)
async def check_income_order_5(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    try:
        await order_rq.set_status(data["order"].id, 'Заказ готов')
        await callback.message.answer('*Заказ был отправлен в архив*', parse_mode='Markdown')
        await state.clear()
    except Exception as e:
        await callback.message.answer(str(e))


@router.callback_query(F.data == 'back', check_orders.close_order)
async def check_income_order_6(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    try:
        await check_income_order_1(data['callback'], data['state'])
    except Exception as e:
        await callback.message.answer(str(e))


@router.callback_query(F.data == 'mark_order')
async def check_income_order_6(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    await order_rq.mark_order(data['order'].id)
    order = await order_rq.get_order(data['order'].id)
    if order.flag:
        await callback.message.answer('Заказ был отмечен')
    else:
        await callback.message.answer('Заказ больше не отмечен')