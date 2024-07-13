from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, InputMediaDocument, FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.id_config import senders
from app.keyboards import async_keyboards as async_kb
from app.keyboards import static_keyboards as static_kb
from app.database.requests import order_request as order_rq
from app.database.requests import shipment_request as ship_rq
from app.database.requests import cheque_request as cheque_rq
from app.database.requests import fish_request as fish_rq

from app.states.order import check_orders

router = Router()


@router.callback_query(F.data == 'view_shipments')
async def check_income_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    await state.set_state(check_orders.select_shipment)
    await callback.message.answer('Выберите поставку:', reply_markup=await async_kb.order_shipments(data['order'].id))


@router.callback_query(F.data.startswith('shipment_id_'), check_orders.select_shipment)
async def check_income_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    shipment_id = str(callback.data)[12:]
    shipment = await ship_rq.get_shipment(shipment_id)
    await state.update_data(shipment_id=shipment_id, shipment=shipment)
    cheque = await cheque_rq.get_cheque(shipment_id)
    fish = await fish_rq.get_fish(shipment_id)
    data = await state.get_data()
    media_list = []
    document_list = []
    caption = (f'*Дата отправки:* _{shipment.create_date}_\n'
               f'*Кол-во товара S:* _{shipment.quantity_s}_ M: _{shipment.quantity_m}_ L: _{shipment.quantity_l}_\n'
               f'*Статус:* _{shipment.status}_\n')
    if shipment.status == 'Поставка отправлена':
        media_list.append(InputMediaPhoto(media=FSInputFile(path=data['order'].order_image), caption=caption, parse_mode="Markdown"))
        media_list.append(InputMediaPhoto(media=FSInputFile(path=cheque.cheque_image_id)))
        media_list.append(InputMediaPhoto(media=FSInputFile(path=fish.fish_image_id)))
        if cheque.payment_image is not None:
            media_list.append(InputMediaPhoto(media=FSInputFile(path=cheque.payment_image)))
        await callback.message.answer_media_group(media=media_list)
        await callback.message.answer('Выберите действие', reply_markup=static_kb.shipment_actions)
    # elif shipment.status == 'Пришла в Москву':
    #     media_list.append(InputMediaPhoto(media=data['order'].order_image, caption=caption, parse_mode="Markdown"))
    #     media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
    #     media_list.append(InputMediaPhoto(media=fish.fish_image_id))
    #     if cheque.payment_image is not None:
    #         media_list.append(InputMediaPhoto(media=cheque.payment_image))
    #     media_list.append(InputMediaPhoto(media=shipment.image_1_id))
    #     await callback.message.answer_media_group(media=media_list)
    #     await callback.message.answer('Выберите действие', reply_markup=static_kb.shipment_actions)
    # elif shipment.status == 'Принята на складе ПД':
    #     media_list.append(InputMediaPhoto(media=data['order'].order_image, caption=caption, parse_mode="Markdown"))
    #     media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
    #     media_list.append(InputMediaPhoto(media=fish.fish_image_id))
    #     if cheque.payment_image is not None:
    #         media_list.append(InputMediaPhoto(media=cheque.payment_image))
    #     media_list.append(InputMediaPhoto(media=shipment.image_1_id))
    #     document_list.append(InputMediaDocument(media=shipment.document_1_id))
    #     await callback.message.answer_media_group(media=media_list)
    #     await callback.message.answer_media_group(media=document_list)
    #     await callback.message.answer('Выберите действие', reply_markup=static_kb.shipment_actions)
    # elif shipment.status == 'Отправлена на склад WB':
    #     media_list.append(InputMediaPhoto(media=data['order'].order_image, caption=caption, parse_mode="Markdown"))
    #     media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
    #     media_list.append(InputMediaPhoto(media=fish.fish_image_id))
    #     if cheque.payment_image is not None:
    #         media_list.append(InputMediaPhoto(media=cheque.payment_image))
    #     media_list.append(InputMediaPhoto(media=shipment.image_1_id))
    #     media_list.append(InputMediaPhoto(media=shipment.image_2_id))
    #     document_list.append(InputMediaDocument(media=shipment.document_1_id))
    #     await callback.message.answer_media_group(media=media_list)
    #     await callback.message.answer_media_group(media=document_list)
    #     await callback.message.answer('Выберите действие', reply_markup=static_kb.shipment_actions)
    # elif shipment.status == 'Принята на складе WB':
    #     media_list.append(InputMediaPhoto(media=data['order'].order_image, caption=caption, parse_mode="Markdown"))
    #     media_list.append(InputMediaPhoto(media=cheque.cheque_image_id))
    #     media_list.append(InputMediaPhoto(media=fish.fish_image_id))
    #     if cheque.payment_image is not None:
    #         media_list.append(InputMediaPhoto(media=cheque.payment_image))
    #     media_list.append(InputMediaPhoto(media=shipment.image_1_id))
    #     media_list.append(InputMediaPhoto(media=shipment.image_2_id))
    #     document_list.append(InputMediaDocument(media=shipment.document_1_id))
    #     document_list.append(InputMediaDocument(media=shipment.document_2_id))
    #     await callback.message.answer_media_group(media=media_list)
    #     await callback.message.answer_media_group(media=document_list)
    #     await callback.message.answer('Выберите действие', reply_markup=static_kb.shipment_actions)
