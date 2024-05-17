from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from app.id_config import senders, recipients
from app.keyboards import static_keyboards as static_kb
from app.keyboards import async_keyboards as async_kb
from app.states.add_article import view_article
from app.database import requests as rq

router = Router()


@router.message(F.text == 'Список артикулов')
async def check_all_orders(message: Message, state: FSMContext):
    if message.from_user.id in senders:
        await state.clear()
        await state.set_state(view_article.select_article)
        await message.answer('Список артикулов:', reply_markup=await async_kb.all_articles_table())


@router.callback_query(F.data.startswith('article_'), view_article.select_article)
async def check_all_orders(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    article = str(callback.data)[8:]
    await state.update_data(article=article)
    article = await rq.get_article(article)
    media_list = []
    media_list.append(InputMediaPhoto(media=article.image_id, caption=f'Артикул {article.article}'))
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
