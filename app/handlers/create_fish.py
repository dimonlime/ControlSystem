import os
from datetime import datetime
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.utils.utils import download_file_func

from app.states.shipment import create_shipment_state, create_fish_state


router = Router()


@router.message(create_fish_state.insert_fish_number)
async def insert_date(message: Message, state: FSMContext):
    try:
        fish_number = int(message.text)
        await state.update_data(fish_number=fish_number)
        await state.set_state(create_fish_state.insert_date)
        await message.answer(f'Введите дату\n'
                             f'Пример: {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}\n')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_fish_state.insert_date)
async def insert_fish_date(message: Message, state: FSMContext):
    try:
        message_date = str(message.text)
        fish_date = datetime.strptime(message_date, "%d-%m-%Y %H:%M:%S")
        if fish_date <= datetime.now():
            await state.update_data(fish_date=fish_date.strftime("%d-%m-%Y %H:%M:%S"))
            await state.set_state(create_fish_state.insert_weight)
            await message.answer('Введите вес в кг:')
        else:
            await message.answer(f'Введите дату не позднее чем {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_fish_state.insert_weight)
async def insert_fish_weight(message: Message, state: FSMContext):
    try:
        weight = int(message.text)
        await state.update_data(fish_weight=weight)
        await state.set_state(create_fish_state.insert_sack_count)
        await message.answer('Введите кол-во мешков:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_fish_state.insert_sack_count)
async def insert_fish_sack_count(message: Message, state: FSMContext):
    try:
        sack_count = int(message.text)
        await state.update_data(fish_sack_count=sack_count)
        await state.set_state(create_fish_state.insert_fish_image)
        await message.answer('Прикрепите фотографию FIS`:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_fish_state.insert_fish_image)
async def insert_fish_image(message: Message, state: FSMContext):
    try:

        folder_path = os.getenv('FIS`_PATH')
        image_id = message.photo[-1].file_id

        path = await download_file_func(image_id, folder_path)

        await state.update_data(fish_image=path)
        await message.answer('Теперь нужно заполнить данные поставки')
        await message.answer('Введите кол-во отправляемого товара размера XS:')
        await state.set_state(create_shipment_state.insert_quantity_xs)
    except TypeError:
        await message.answer('Ошибка, попробуйте еще раз')