import os

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.id_config import senders
from app.states.product_card import create_product_card
from app.database.requests import product_card_request as card_rq

from app.utils.utils import download_file_func


router = Router()


@router.message(F.text == 'Добавить карту товара')
async def add_article(message: Message, state: FSMContext):
    if message.from_user.id in senders:
        await state.set_state(create_product_card.insert_article)
        await message.answer('Введите артикул:')


@router.message(create_product_card.insert_article)
async def insert_article_id(message: Message, state: FSMContext):
    article = str(message.text)
    await state.update_data(article=article)
    await state.set_state(create_product_card.insert_vendor_internal_article)
    await message.answer('Введите внутренний артикул поставщика:')


@router.message(create_product_card.insert_vendor_internal_article)
async def insert_article_id(message: Message, state: FSMContext):
    vendor_internal_article = str(message.text)
    await state.update_data(vendor_internal_article=vendor_internal_article)
    await state.set_state(create_product_card.insert_color)
    await message.answer('Введите цвет товара:')


@router.message(create_product_card.insert_color)
async def insert_article_id(message: Message, state: FSMContext):
    color = str(message.text)
    await state.update_data(color=color)
    await state.set_state(create_product_card.insert_shop_name)
    await message.answer('Введите название магазина:')


@router.message(create_product_card.insert_shop_name)
async def insert_article_id(message: Message, state: FSMContext):
    shop_name = str(message.text)
    await state.update_data(shop_name=shop_name)
    await state.set_state(create_product_card.insert_image)
    await message.answer('Прикрепите фотографию товара:')


@router.message(create_product_card.insert_image)
async def insert_article_image(message: Message, state: FSMContext):
    try:
        folder_path = os.getenv('PRODUCT_CARD_PATH')
        image_id = message.photo[-1].file_id
        await state.update_data(image_id=image_id)


        # file = await bot.get_file(image_id)
        # destination = folder_path
        # destination_file = os.path.join(destination, file.file_unique_id + '.jpg')
        # await bot.download_file(file.file_path, destination_file)
        #
        # relative_path = rf'{folder_path}\{file.file_unique_id}.jpg'
        # absolute_path = os.path.abspath(relative_path)

        path = await download_file_func(image_id, folder_path)

        data = await state.get_data()
        await card_rq.create_product_card(data['article'], data['vendor_internal_article'], data['color'], data['shop_name'], path)
        await message.answer('Карточка товара успешно создана')
        await state.clear()
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')
