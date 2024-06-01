from datetime import datetime

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, InputMediaDocument
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.id_config import senders
from app.keyboards import async_keyboards as async_kb
from app.keyboards import static_keyboards as static_kb
from app.database.requests import order_request as order_rq
from app.utils.utils import enough_quantity_order, shipments_quantity_s, shipments_quantity_m, shipments_quantity_l, shipments_ready

from app.states.order import archive_orders

router = Router()


@router.message(F.text == 'Архив заказов')
async def check_all_orders(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in senders:
        await state.set_state(archive_orders.select_order)
        await message.answer('Выберите заказ:', reply_markup=await async_kb.archive_orders())


@router.callback_query(F.data.startswith('order_id_'), archive_orders.select_order)
async def check_income_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    order_id = str(callback.data)[9:]
    order = await order_rq.get_order(order_id)
    await state.update_data(order=order)
    ship_s = await shipments_quantity_s(order_id)
    ship_m = await shipments_quantity_m(order_id)
    ship_l = await shipments_quantity_l(order_id)
    order_create_date = datetime.strptime(order.create_date, "%d-%m-%Y %H:%M:%S")
    caption = (f'*Артикул:* _{order.internal_article}_\n'
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
        caption += f'🔴 *Ожидается* *S:* _{remain_s}_ *M:* _{remain_m}_ *L:* _{remain_l}_\n'
    else:
        caption += f'🟢 *Заказанное кол-во отправлено*\n'
    if not await shipments_ready(order_id):
        caption += f'🔴 *Не все поставки приняты на складе WB*\n'
    else:
        caption += f'🟢 *Все текущие поставки приняты на складе WB*\n'
    media_list = [InputMediaPhoto(media=order.order_image, caption=caption, parse_mode="Markdown")]
    await callback.message.answer_media_group(media=media_list)
    await callback.message.answer(f'Выберите действие', reply_markup=static_kb.order_actions)
