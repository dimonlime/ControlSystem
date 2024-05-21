from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from app.id_config import senders, recipients
from app.keyboards import static_keyboards as static_kb
from app.keyboards import async_keyboards as async_kb
from app.states.product_card import view_product_card
from app.database import requests as rq

router = Router()


@router.message(F.text == 'Список карт товара')
async def check_all_orders(message: Message, state: FSMContext):
    if message.from_user.id in senders:
        await state.clear()
        await state.set_state(view_product_card.select_article)
        await message.answer('Выберите артикул:', reply_markup=await async_kb.all_articles_table())


@router.callback_query(F.data.startswith('article_'), view_product_card.select_article)
async def check_all_orders(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    card_id = str(callback.data)[8:]
    await state.update_data(card_id=card_id)
    product_card = await rq.get_product_card(card_id)
    media_list = []
    media_list.append(InputMediaPhoto(media=product_card.image_id, caption=f'Артикул: {product_card.article}\n'
                                                                      f'Внутренний артикул поставщика: {product_card.vendor_internal_article}\n'
                                                                      f'Цвет: {product_card.color}\n'
                                                                      f'Название магазина: {product_card.shop_name}'
                                      ))
    await callback.message.answer_media_group(media=media_list)
    # await state.set_state(view_article.replace_image)
    # await callback.message.answer('Выберите действие', reply_markup=static_kb.action_article_keyboard)

# @router.callback_query(F.data.startswith('replace_image'))
# async def check_all_orders(callback: CallbackQuery, state: FSMContext):
#     await callback.answer()
#     await callback.message.answer('Прикрепите новое фото:')
#     await state.set_state(view_article.insert_image)
#
#
# @router.message(view_article.insert_image)
# async def check_all_orders(message: Message, state: FSMContext):
#     try:
#         image_id = message.photo[-1].file_id
#         await state.update_data(image_id=image_id)
#         data = await state.get_data()
#         await rq.edit_image_article(data['article'], data['image_id'])
#         await message.answer('Фото успешно обновлено')
#         await state.set_state(view_article.select_article)
#     except ValueError:
#         await message.answer('Ошибка, попробуйте еще раз')
