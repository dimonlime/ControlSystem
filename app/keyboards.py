from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app import id_config
from app.database import requests as rq
import json

recipient_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Изменить статус заказа')],
    [KeyboardButton(text='Проверить чеки')]

], resize_keyboard=True)

sender_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Создать заказ')],
    [KeyboardButton(text='Просмотреть чеки')],
    [KeyboardButton(text='Посмотреть заказы')]
], resize_keyboard=True)

vendor_internal_article = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пропустить', callback_data='skip')]
])

cheques_category = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Все чеки', callback_data='all_chques')],
    [InlineKeyboardButton(text='Чеки с отсрочкой', callback_data='delay_cheques')],
    [InlineKeyboardButton(text='Горящие чеки', callback_data='fire_cheques')]
])

cheques_category_2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Не оплаченные чеки', callback_data='unpaid_cheques')],
    [InlineKeyboardButton(text='Оплаченные чеки', callback_data='paid_cheques')]
])

select_cheque = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Оплатить чек', callback_data='pay_cheque')],
    [InlineKeyboardButton(text='Данные заказа', callback_data='order_info')],
    [InlineKeyboardButton(text='Данные чека', callback_data='cheque_info')],
    [InlineKeyboardButton(text='Данные fish', callback_data='fish_info')],
    [InlineKeyboardButton(text='Фактические данные', callback_data='fact_info')],
    [InlineKeyboardButton(text='Все данные', callback_data='all_info')]
])


view_info = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Данные заказа', callback_data='order_info')],
    [InlineKeyboardButton(text='Данные чека', callback_data='cheque_info')],
    [InlineKeyboardButton(text='Данные fish', callback_data='fish_info')],
    [InlineKeyboardButton(text='Фактические данные', callback_data='fact_info')],
    [InlineKeyboardButton(text='Все данные', callback_data='all_info')]
])


async def inline_sending_method():
    keyboard = InlineKeyboardBuilder()
    for method in id_config.sending_method:
        keyboard.add(InlineKeyboardButton(text=method, callback_data=f'method_{method}'))
    return keyboard.adjust(3).as_markup()


async def inline_order_status():
    keyboard = InlineKeyboardBuilder()
    for status in id_config.order_status:
        keyboard.add(InlineKeyboardButton(text=status, callback_data=f'status_{status}'))
    return keyboard.adjust(1).as_markup()


async def inline_all_orders(income_id):
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_orders()
    for order in data:
        today_date = datetime.now()
        half_year = today_date - timedelta(days=365 / 2)
        order_date = datetime.strptime(order.date, "%d-%m-%Y %H:%M:%S")
        if half_year <= order_date <= today_date:
            if order.delivery_id == income_id:
                keyboard.add(InlineKeyboardButton(text=f'Арт: "{order.internal_article}", Дата: "{order.date}"',
                                                  callback_data=f'edit_status_{order.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_all_cheques():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_cheques()
    for cheque in data:
        today_date = datetime.now()
        half_year = today_date - timedelta(days=365 / 2)
        cheque_date = datetime.strptime(cheque.cheque_date, "%d-%m-%Y %H:%M")
        if half_year <= cheque_date <= today_date:
            keyboard.add(InlineKeyboardButton(text=f'Номер чека: "{cheque.cheque_number}", Цена: "{cheque.price}"',
                                              callback_data=f'pay_cheque_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_delay_cheques():
    keyboard = InlineKeyboardBuilder()
    data = await rq.delay_cheques()
    for cheque in data:
        today_date = datetime.now()
        half_year = today_date - timedelta(days=365/2)
        cheque_date = datetime.strptime(cheque.cheque_date, "%d-%m-%Y %H:%M")
        if half_year <= cheque_date <= today_date:
            keyboard.add(InlineKeyboardButton(text=f'Номер чека: "{cheque.cheque_number}", Цена: "{cheque.price}"',
                                              callback_data=f'pay_cheque_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_fire_cheques():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_cheques()
    for cheque in data:
        cheque_date = datetime.strptime(cheque.cheque_date, "%d-%m-%Y %H:%M")
        today_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        today_date_valid = datetime.strptime(today_date, "%d-%m-%Y %H:%M:%S")
        half_year = today_date_valid - timedelta(days=365 / 2)
        if half_year <= cheque_date <= today_date_valid:
            if cheque.cheque_status == 'Чек не оплачен по истечению 2 недель':
                keyboard.add(InlineKeyboardButton(text=f'Номер чека: "{cheque.cheque_number}", Цена: "{cheque.price}"',
                                                  callback_data=f'pay_cheque_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_unpaid_cheques():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_cheques()
    for cheque in data:
        today_date = datetime.now()
        half_year = today_date - timedelta(days=365 / 2)
        cheque_date = datetime.strptime(cheque.cheque_date, "%d-%m-%Y %H:%M")
        if half_year <= cheque_date <= today_date:
            if cheque.cheque_status == 'По чеку имеется отсрочка' or cheque.cheque_status == 'Чек не оплачен по истечению 2 недель':
                keyboard.add(InlineKeyboardButton(text=f'Номер чека: "{cheque.cheque_number}", Цена: "{cheque.price}"',
                                                  callback_data=f'view_cheque_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_paid_cheques():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_cheques()
    for cheque in data:
        today_date = datetime.now()
        half_year = today_date - timedelta(days=365 / 2)
        cheque_date = datetime.strptime(cheque.cheque_date, "%d-%m-%Y %H:%M")
        if half_year <= cheque_date <= today_date:
            if cheque.cheque_status == 'Чек оплачен':
                keyboard.add(InlineKeyboardButton(text=f'Номер чека: "{cheque.cheque_number}", Цена: "{cheque.price}"',
                                                  callback_data=f'view_cheque_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_all_orders_send(income_id):
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_orders()
    for order in data:
        today_date = datetime.now()
        half_year = today_date - timedelta(days=365 / 2)
        order_date = datetime.strptime(order.date, "%d-%m-%Y %H:%M:%S")
        if half_year <= order_date <= today_date:
            if order.delivery_id == income_id:
                keyboard.add(InlineKeyboardButton(text=f'Арт: "{order.internal_article}"; Дата: "{order.date}"',
                                                  callback_data=f'get_info_{order.id}'))
    return keyboard.adjust(1).as_markup()


async def all_incomes():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_orders()
    incomes = []
    for order in data:
        today_date = datetime.now()
        half_year = today_date - timedelta(days=365 / 2)
        order_date = datetime.strptime(order.date, "%d-%m-%Y %H:%M:%S")
        if half_year <= order_date <= today_date:
            if order.delivery_id not in incomes:
                incomes.append(order.delivery_id)
    for income in incomes:
        keyboard.add(InlineKeyboardButton(text=f'ID Поставки: {income}',
                                          callback_data=f'income_{income}'))
    return keyboard.adjust(1).as_markup()

async def all_incomes_recipients():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_orders()
    incomes = []
    for order in data:
        today_date = datetime.now()
        half_year = today_date - timedelta(days=365 / 2)
        order_date = datetime.strptime(order.date, "%d-%m-%Y %H:%M:%S")
        if half_year <= order_date <= today_date:
            if order.delivery_id not in incomes:
                incomes.append(order.delivery_id)
    for income in incomes:
        keyboard.add(InlineKeyboardButton(text=f'ID Поставки: {income}',
                                          callback_data=f'income_rec{income}'))
    return keyboard.adjust(1).as_markup()
