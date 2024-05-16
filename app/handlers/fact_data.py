from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.database import requests as rq

from app.states.create_cheque import create_cheque_state

router = Router()


"""Заполнение фактических данных + переход на заполнение fish-------------------------------------------------------"""


@router.message(create_cheque_state.insert_fact_s)
async def insert_fact_s(message: Message, state: FSMContext):
    try:
        fact_s = int(message.text)
        await state.update_data(fact_s=fact_s)
        await state.set_state(create_cheque_state.insert_fact_m)
        await message.answer('Введите фактическое кол-во товара размера M')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_fact_m)
async def insert_fact_m(message: Message, state: FSMContext):
    try:
        fact_m = int(message.text)
        await state.update_data(fact_m=fact_m)
        await state.set_state(create_cheque_state.insert_fact_l)
        await message.answer('Введите фактическое кол-во товара размера L')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


@router.message(create_cheque_state.insert_fact_l)
async def insert_fact_l(message: Message, state: FSMContext):
    try:
        fact_l = int(message.text)
        await state.update_data(fact_l=fact_l)
        data = await state.get_data()
        await rq.insert_fact(data['order_id'], data['fact_s'], data['fact_m'], data['fact_l'], )
        await message.answer('Фактические данные введены успешно')
        await state.set_state(create_cheque_state.insert_fish)
        await message.answer('Внимание, чтобы поменить статус, нужно приложить FISH')
        await message.answer('Введите номер FISH для данного заказа:')
    except ValueError:
        await message.answer('Ошибка, попробуйте еще раз')


