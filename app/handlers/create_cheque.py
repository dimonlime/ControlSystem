import os
from datetime import datetime
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.utils.utils import download_file_func

from app.states.shipment import create_cheque_state, create_fish_state


router = Router()


@router.message(create_cheque_state.insert_date)
async def insert_date(message: Message, state: FSMContext):
    try:
        message_date = str(message.text)
        cheque_date = datetime.strptime(message_date, "%d-%m-%Y %H:%M")
        if cheque_date <= datetime.now():
            await state.update_data(cheque_date=cheque_date.strftime("%d-%m-%Y %H:%M:%S"))
            await state.set_state(create_cheque_state.insert_cheque_number)
            await message.answer('Введите номер чека:')
        else:
            await message.answer(f'Введите дату не позднее чем {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_cheque_number)
async def insert_number(message: Message, state: FSMContext):
    try:
        cheque_number = int(message.text)
        await state.update_data(cheque_number=cheque_number)
        await state.set_state(create_cheque_state.insert_vendor_internal_article)
        await message.answer('Введите артикул поставщика:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_vendor_internal_article)
async def insert_number(message: Message, state: FSMContext):
    try:
        vendor_article = int(message.text)
        await state.update_data(cheque_vendor_article=vendor_article)
        await state.set_state(create_cheque_state.insert_price)
        await message.answer('Введите цену:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_price)
async def insert_price_cheque(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(cheque_price=price)
        await state.set_state(create_cheque_state.insert_cheque_image)
        await message.answer('Отправьте фотографию чека:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_cheque_image)
async def insert_image_cheque(message: Message, state: FSMContext):
    try:

        folder_path = os.getenv('CHEQUE_PATH')
        image_id = message.photo[-1].file_id

        path = await download_file_func(image_id, folder_path)

        await state.update_data(cheque_image=path)
        await state.update_data(cheque_create_date=datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        await message.answer('Теперь нужно заполнить FIS` для поставки')
        await message.answer('Введите номер FIS`:')
        await state.set_state(create_fish_state.insert_fish_number)
    except TypeError:
        await message.answer('Ошибка, попробуйте еще раз')