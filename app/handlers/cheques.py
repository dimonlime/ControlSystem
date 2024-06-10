from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.id_config import senders, recipients
from app.keyboards import static_keyboards as static_kb
from app.keyboards import async_keyboards as async_kb
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, InputMediaDocument
from app.database.requests import cheque_request as cheque_rq
from app.database.requests import order_request as order_rq
from app.database.requests import fish_request as fish_rq
from app.database.requests import shipment_request as ship_rq
from app.states.cheque import view_cheque_state

router = Router()


@router.message(F.text == 'Горящие чеки')
async def check_all_orders(message: Message, state: FSMContext):
    await state.set_state(view_cheque_state.select_cheque)
    await message.answer('Список горящих чеков:', reply_markup=await async_kb.fire_cheques())


@router.message(F.text == 'Чеки с отсрочкой')
async def check_all_orders(message: Message, state: FSMContext):
    await state.set_state(view_cheque_state.select_cheque)
    await message.answer('Список чеков с отсрочкой:', reply_markup=await async_kb.delay_cheques())


@router.message(F.text == 'Архив чеков')
async def check_all_orders(message: Message, state: FSMContext):
    await state.set_state(view_cheque_state.select_cheque)
    await message.answer('Список оплаченных чеков:', reply_markup=await async_kb.paid_cheques())


@router.callback_query(F.data.startswith('cheque_id_'), view_cheque_state.select_cheque)
async def view_cheque(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    cheque_id = str(callback.data)[10:]
    cheque = await cheque_rq.get_cheque_2(cheque_id)
    shipment = await ship_rq.get_shipment(cheque.shipment_id)
    order = await order_rq.get_order(shipment.order_id)
    await state.update_data(cheque=cheque, order=order, shipment=shipment)
    reply_markup = None
    caption = (f'*Цена* _{cheque.price}_*$*\n'
               f'*Дата* _{cheque.date}_\n'
               f'*Арт:* _{order.internal_article}_\n'
               f'*S:* _{shipment.quantity_s}_ *M:* _{shipment.quantity_m}_ *L:* _{shipment.quantity_l}_\n')
    if callback.from_user.id in senders:
        reply_markup = static_kb.pay_cheque
    elif callback.from_user.id in recipients:
        reply_markup = None
    if cheque.cheque_status == 'Чек не оплачен по истечению 2-ух недель':
        caption += f'🔴*Статус:* _{cheque.cheque_status}_'
    elif cheque.cheque_status == 'По чеку имеется отсрочка':
        caption += f'🟠*Статус:* _{cheque.cheque_status}_'
    await callback.message.answer_photo(caption=caption,
                                        photo=cheque.cheque_image_id, reply_markup=reply_markup, parse_mode="Markdown")


@router.callback_query(F.data == 'pay_cheque')
async def view_cheque(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Прикрепите скрин оплаты:')
    await state.set_state(view_cheque_state.insert_payment_image)


@router.message(view_cheque_state.insert_payment_image)
async def check_all_orders(message: Message, state: FSMContext):
    try:
        payment_image_id = message.photo[-1].file_id
        data = await state.get_data()
        await cheque_rq.insert_payment_image(data['cheque'].id, payment_image_id)
        await message.answer('Чек оплачен успешно')
        cheque = await cheque_rq.get_cheque_2(data['cheque'].id)
        await state.update_data(cheque=cheque)
        data = await state.get_data()
        for chat_id in recipients:
            if chat_id != message.chat.id:
                media_list = [InputMediaPhoto(media=data['cheque'].cheque_image_id,
                                              caption=f'🔴*Оповещение об оплате чека*🔴\n'
                                                      f"*Арт:* _{data['order'].internal_article}_\n"
                                                      f"*Цена:* _{data['cheque'].price}_*$*\n"
                                                      f"*Дата чека:* _{data['cheque'].date}_\n"
                                                      f"*Кол-во товара* *S:* _{data['shipment'].quantity_s}_ *M:* _{data['shipment'].quantity_m}_ *L:* _{data['shipment'].quantity_l}_\n",
                                              parse_mode="Markdown"),
                              InputMediaPhoto(media=data['cheque'].payment_image)]
                await message.bot.send_media_group(media=media_list, chat_id=chat_id)
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.callback_query(F.data.startswith('paid_cheque_id_'), view_cheque_state.select_cheque)
async def view_cheque(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    cheque_id = str(callback.data)[15:]
    cheque = await cheque_rq.get_cheque_2(cheque_id)
    shipment = await ship_rq.get_shipment(cheque.shipment_id)
    order = await order_rq.get_order(shipment.order_id)
    media_list = []
    media_list.append(InputMediaPhoto(media=cheque.cheque_image_id,
                                      caption=
                                      f'*Цена* _{cheque.price}_*$*\n'
                                      f'*Дата* _{cheque.date}_\n'
                                      f'*Арт:* _{order.internal_article}_\n'
                                      f'*S:* _{shipment.quantity_s}_ *M:* _{shipment.quantity_m}_ *L:* _{shipment.quantity_l}_\n'
                                      f'🟢*Статус:* _{cheque.cheque_status}_', parse_mode="Markdown"))
    media_list.append(InputMediaPhoto(media=cheque.payment_image))
    await callback.message.answer_media_group(media=media_list)
