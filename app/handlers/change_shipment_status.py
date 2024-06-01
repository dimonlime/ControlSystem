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
from app.database.requests import fish_request as fish_rq
from app.database.requests import cheque_request as cheque_rq
from app.utils.utils import enough_quantity_order, shipments_ready

from app.states.shipment import change_shipment_status_state

router = Router()


@router.message(F.text == 'Изменить статус поставки')
async def check_all_orders(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in senders:
        await state.set_state(change_shipment_status_state.select_shipment)
        await message.answer('Выберите поставку:', reply_markup=await async_kb.change_status_shipments())


@router.callback_query(F.data.startswith('shipment_id_'), change_shipment_status_state.select_shipment)
async def check_income_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    shipment_id = str(callback.data)[12:]
    await state.update_data(shipment_id=shipment_id)
    shipment = await ship_rq.get_shipment(shipment_id)
    order = await order_rq.get_order(shipment.order_id)
    await state.set_state(change_shipment_status_state.select_status)
    await callback.message.answer_photo(photo=order.order_image,
                                        caption=f'*Поставка №*_{shipment.id}_\n'
                                                f'*Отправлено* *S:* _{shipment.quantity_s}_ *M:* _{shipment.quantity_m}_ *L:* _{shipment.quantity_l}_\n'
                                                f'*Статус:* _{shipment.status}_\n',
                                        reply_markup=await async_kb.shipment_status(), parse_mode="Markdown")


@router.callback_query(F.data.startswith('status_'), change_shipment_status_state.select_status)
async def check_income_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    shipment_status = str(callback.data)[7:]
    data = await state.get_data()
    shipment = await ship_rq.get_shipment(data['shipment_id'])
    await state.update_data(shipment_status=shipment_status)
    if shipment_status == 'Пришла в Москву' and shipment.status == 'Поставка отправлена':
        await state.set_state(change_shipment_status_state.insert_image_1)
        await callback.message.answer('Прикрепите фото:')
    elif shipment_status == 'Принята на складе ПД' and shipment.status == 'Пришла в Москву':
        await state.set_state(change_shipment_status_state.insert_document_1)
        await callback.message.answer('Прикрепите документ:')
    elif shipment_status == 'Отправлена на склад WB' and shipment.status == 'Принята на складе ПД':
        await state.set_state(change_shipment_status_state.insert_image_2)
        await callback.message.answer('Прикрепите фото:')
    elif shipment_status == 'Принята на складе WB' and shipment.status == 'Отправлена на склад WB':
        await state.set_state(change_shipment_status_state.insert_document_2)
        await callback.message.answer('Прикрепите документ:')
    else:
        await callback.message.answer('Нельзя выполнить действие')


@router.message(change_shipment_status_state.insert_image_1)
async def insert_cheque_date(message: Message, state: FSMContext):
    try:
        image_id = message.photo[-1].file_id
        data = await state.get_data()
        await ship_rq.insert_image_1(data['shipment_id'], image_id)
        await ship_rq.set_status(data['shipment_id'], data['shipment_status'])
        await message.answer('Статус успешно обновлен')
        await state.set_state(change_shipment_status_state.select_status)
    except Exception:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(change_shipment_status_state.insert_document_1)
async def insert_cheque_date(message: Message, state: FSMContext):
    try:
        file_id = message.document.file_id
        data = await state.get_data()
        await ship_rq.insert_document_1(data['shipment_id'], file_id)
        await ship_rq.set_status(data['shipment_id'], data['shipment_status'])
        await message.answer('Статус успешно обновлен')
        await state.set_state(change_shipment_status_state.select_status)
    except Exception:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(change_shipment_status_state.insert_image_2)
async def insert_cheque_date(message: Message, state: FSMContext):
    try:
        image_id = message.photo[-1].file_id
        data = await state.get_data()
        await ship_rq.insert_image_2(data['shipment_id'], image_id)
        await ship_rq.set_status(data['shipment_id'], data['shipment_status'])
        await message.answer('Статус успешно обновлен')
        await state.set_state(change_shipment_status_state.select_status)
    except Exception:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(change_shipment_status_state.insert_document_2)
async def insert_cheque_date(message: Message, state: FSMContext):
    try:
        file_id = message.document.file_id
        data = await state.get_data()
        await ship_rq.insert_document_2(data['shipment_id'], file_id)
        await ship_rq.set_status(data['shipment_id'], data['shipment_status'])
        await message.answer('Статус успешно обновлен')
        shipment = await ship_rq.get_shipment(data['shipment_id'])
        if await enough_quantity_order(shipment.order_id):
            if await shipments_ready(shipment.order_id):
                await order_rq.set_status(shipment.order_id, 'Заказ готов')
        await state.set_state(change_shipment_status_state.select_status)
    except Exception:
        await message.answer('Ошибка, попробуйте еще раз')