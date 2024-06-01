from datetime import datetime
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from app.id_config import senders
from app.keyboards import async_keyboards as async_kb
from app.keyboards import static_keyboards as static_kb
from app.database.requests import order_request as order_rq
from app.database.requests import product_card_request as card_rq
from app.utils.utils import product_card_exists

from app.states.create_order import create_order_state

router = Router()

"""Создание заказа--------------------------------------------------------------------------------------------------"""


@router.message(F.text == 'Создать заказ')
async def create_order(message: Message, state: FSMContext):
    if message.from_user.id in senders:
        await state.set_state(create_order_state.insert_internal_article)
        await message.answer('Выберите внутренний артикул товара:', reply_markup=await async_kb.all_product_cards())


@router.callback_query(F.data.startswith('article_'), create_order_state.insert_internal_article)
async def insert_internal_article(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        internal_article = str(callback.data)[8:]
        if await product_card_exists(internal_article):
            product_card = await card_rq.get_product_card(internal_article)
            await state.update_data(internal_article=internal_article)
            await state.update_data(vendor_internal_article=product_card.vendor_internal_article)
            await state.update_data(color=product_card.color)
            await state.update_data(shop_name=product_card.shop_name)
            await state.update_data(order_image=product_card.image_id)
            await state.set_state(create_order_state.insert_s_order)
            await callback.message.answer('Введите кол-во товара размера S:')
        else:
            await callback.message.answer('Для данного артикула не создана карточка товара, воспользуйтесь командой '
                                          '/create_product_card, чтобы создать ее')
    except ValueError:
        await callback.message.answer('Ошибка, попробуйте еще раз')


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
        await state.set_state(create_order_state.insert_sending_method)
        await message.answer('Введите тип отправки:', reply_markup=await async_kb.sending_method())
    except ValueError:
        await message.answer('Введите целое число')


@router.callback_query(F.data.startswith('method_'), create_order_state.insert_sending_method)
async def choose_sending_method(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    sending_method = str(callback.data)
    await state.update_data(sending_method=sending_method[7:])
    await insert_image_auto(callback.message, state)


@router.message(create_order_state.create_order)
async def insert_image_auto(message: Message, state: FSMContext):
    create_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    change_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    await state.update_data(create_date=create_date)
    await state.update_data(change_date=change_date)
    data = await state.get_data()
    await order_rq.create_order_db(data['create_date'], data['change_date'], data['internal_article'], data['vendor_internal_article'],
                                   data['quantity_s'], data['quantity_m'], data['quantity_l'], data['color'], data['shop_name'],
                                   data['sending_method'], data['order_image'])
    await message.answer('Заказ создан успешно')
    for chat_id in senders:
        if chat_id != message.chat.id:
            media_list = [InputMediaPhoto(media=data['order_image'],
                                          caption=f'🔴*Оповещение о создании заказа*🔴\n'
                                                  f"*Артикул:* _{data['internal_article']}_\n"
                                                  f"*Дата создания заказа:* _{data['create_date']}_\n"
                                                  f"*Кол-во товара* *S:* _{data['quantity_s']}_ *M:* _{data['quantity_m']}_ *L:* _{data['quantity_l']}_\n",
                                          parse_mode="Markdown")]
            await message.bot.send_media_group(media=media_list, chat_id=chat_id)
    await state.clear()
