from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.id_config import senders, recipients
from app.keyboards import static_keyboards as static_kb
from app.states.add_article import create_article
from app.database import requests as rq

router = Router()


@router.message(F.text == 'Добавить артикул')
async def add_article(message: Message, state: FSMContext):
    if message.from_user.id in senders:
        await state.set_state(create_article.insert_article)
        await message.answer('Введите артикул:')


@router.message(create_article.insert_article)
async def insert_article_id(message: Message, state: FSMContext):
    article = str(message.text)
    await state.update_data(article=article)
    await state.set_state(create_article.insert_image)
    await message.answer('Прикрепите фото для артикула:')


@router.message(create_article.insert_image)
async def insert_article_image(message: Message, state: FSMContext):
    try:
        image_id = message.photo[-1].file_id
        await state.update_data(image_id=image_id)
        data = await state.get_data()
        await rq.create_article(data['article'], data['image_id'])
        await message.answer('Артикул успешно добавлен')
        await state.clear()
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')
