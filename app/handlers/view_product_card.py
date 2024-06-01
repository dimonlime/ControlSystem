from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from app.id_config import senders, recipients
from app.keyboards import static_keyboards as static_kb
from app.keyboards import async_keyboards as async_kb
from app.states.product_card import view_product_card
from app.database.requests import product_card_request as card_rq


router = Router()


@router.message(F.text == 'Список карт товара')
async def check_all_orders(message: Message, state: FSMContext):
    if message.from_user.id in senders:
        await state.clear()
        await state.set_state(view_product_card.select_article)
        await message.answer('Выберите артикул:', reply_markup=await async_kb.all_product_cards())


@router.callback_query(F.data.startswith('article_'), view_product_card.select_article)
async def check_all_orders(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    card_id = str(callback.data)[8:]
    await state.update_data(card_id=card_id)
    product_card = await card_rq.get_product_card(card_id)
    media_list = []
    media_list.append(InputMediaPhoto(media=product_card.image_id,
                                      caption=f'*Артикул:* _{product_card.article}_\n'
                                              f'*Внутренний артикул поставщика:* _{product_card.vendor_internal_article}_\n'
                                              f'*Цвет:* _{product_card.color}_\n'
                                              f'*Название магазина:* _{product_card.shop_name}_',
                                      parse_mode="Markdown"))
    await callback.message.answer_media_group(media=media_list)