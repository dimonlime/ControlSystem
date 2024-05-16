from datetime import datetime
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.database import requests as rq

from app.states.create_cheque import create_cheque_state

router = Router()

"""Создание fish----------------------------------------------------------------------------------------------------"""


@router.message(create_cheque_state.insert_fish)
async def insert_fish(message: Message, state: FSMContext):
    try:
        fish = int(message.text)
        await state.update_data(fish=fish)
        await state.set_state(create_cheque_state.insert_fish_date)
        await message.answer('Введите дату(пример 03-03-2023 23:23:23')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_fish_date)
async def insert_fish_date(message: Message, state: FSMContext):
    try:
        message_date = str(message.text)
        fish_date = datetime.strptime(message_date, "%d-%m-%Y %H:%M:%S")
        if fish_date <= datetime.now():
            await state.update_data(fish_date=fish_date.strftime("%d-%m-%Y %H:%M:%S"))
            await state.set_state(create_cheque_state.insert_fish_weight)
            await message.answer('Введите вес в кг:')
        else:
            await message.answer(f'Введите дату не позднее чем {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_fish_weight)
async def insert_fish_weight(message: Message, state: FSMContext):
    try:
        weight = int(message.text)
        await state.update_data(weight=weight)
        await state.set_state(create_cheque_state.insert_sack_count)
        await message.answer('Введите кол-во мешков:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_sack_count)
async def insert_fish_sack_count(message: Message, state: FSMContext):
    try:
        sack_count = int(message.text)
        await state.update_data(sack_count=sack_count)
        await state.set_state(create_cheque_state.insert_fish_image_id)
        await message.answer('Прикрепите фотографию FISH:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_fish_image_id)
async def insert_fish_image(message: Message, state: FSMContext):
    try:
        await state.update_data(fish_image=message.photo[-1].file_id)
        await state.update_data(order_change_date=datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        data = await state.get_data()
        order = await rq.get_order(data['order_id'])
        await rq.create_fish(data['fish'], data['fish_date'], data['weight'], data['sack_count'], order.sending_method,
                             data['fish_image'], data['order_id'])
        await rq.set_order_fish(data['order_id'], data['fish'])
        await rq.edit_order_status(data['order_id'], data['order_status'], data['order_change_date'])
        await message.answer('FISH прикрплен')
        await message.answer(f'Статус заказа изменен на {data["order_status"]}')
        await state.clear()
    except TypeError:
        await message.answer('Ошибка, попробуйте еще раз')
